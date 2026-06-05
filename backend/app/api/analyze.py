from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from app.ml.text_analyzer import analyze_text, calculate_behavioral_risk
from app.ml.url_analyzer import analyze_url
from app.ml.voice_analyzer import analyze_voice_transcript, analyze_speech_audio
from app.ml.model_loader import get_model
from app.services.risk_scorer import calculate_risk_score
from app.utils.firebase import save_analysis, check_crowd_database

router = APIRouter()
logger = logging.getLogger(__name__)


class TextAnalysisRequest(BaseModel):
    text: str
    sender: Optional[str] = None
    message_type: Optional[str] = "sms"  # sms, email, chat
    sender_phone: Optional[str] = None
    is_unknown_sender: Optional[bool] = False
    is_international: Optional[bool] = False
    message_frequency: Optional[int] = 1

    @validator('text')
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v


class URLAnalysisRequest(BaseModel):
    url: str
    context: Optional[str] = None


class EmailAnalysisRequest(BaseModel):
    subject: str
    body: str
    sender_email: Optional[str] = None
    has_attachments: Optional[bool] = False
    reply_to: Optional[str] = None


class VoiceTranscriptRequest(BaseModel):
    transcript: str
    caller_id: Optional[str] = None
    call_duration: Optional[int] = None


class BulkAnalysisRequest(BaseModel):
    items: List[Dict[str, str]]
    analysis_type: str = "text"


@router.post("/text")
async def analyze_text_message(request: TextAnalysisRequest):
    """Analyze SMS/text message for scam detection."""
    try:
        model = get_model('text')
        if not model:
            raise HTTPException(status_code=503, detail="ML model not loaded")

        # Text analysis
        text_result = analyze_text(request.text, model)

        # Behavioral analysis
        behavioral_result = calculate_behavioral_risk(
            message_frequency=request.message_frequency or 1,
            unusual_timing=False,
            unknown_sender=request.is_unknown_sender or False,
            international_source=request.is_international or False,
            previous_reports=0
        )

        # Check crowd database
        crowd_check = {"found": False, "report_count": 0}
        if request.sender_phone:
            crowd_check = check_crowd_database(phone=request.sender_phone)
            if crowd_check.get('found'):
                behavioral_result['behavioral_risk_score'] = min(
                    100, behavioral_result['behavioral_risk_score'] + crowd_check['report_count'] * 10
                )

        # Composite risk score
        risk_result = calculate_risk_score(
            text_analysis=text_result,
            behavioral_analysis=behavioral_result,
            sender_info={
                'is_unknown': request.is_unknown_sender,
                'is_international': request.is_international,
                'report_count': crowd_check.get('report_count', 0)
            }
        )

        result = {
            "type": "text_analysis",
            "input": request.text[:200] + "..." if len(request.text) > 200 else request.text,
            "message_type": request.message_type,
            "is_scam": text_result['is_scam'],
            "confidence": text_result['confidence'],
            "scam_type": text_result.get('scam_type'),
            "risk_score": risk_result['overall_risk_score'],
            "risk_level": risk_result['risk_level'],
            "risk_breakdown": risk_result['risk_breakdown'],
            "explanation": text_result['explanation'],
            "keyword_analysis": text_result.get('keyword_analysis', {}),
            "behavioral_analysis": behavioral_result,
            "recommendation": risk_result['recommendation'],
            "crowd_database": crowd_check,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Save to database
        save_data = {**result, "scam_type": text_result.get('scam_type')}
        save_analysis("analysis_history", save_data)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/url")
async def analyze_url_safety(request: URLAnalysisRequest):
    """Analyze URL for phishing and scam indicators."""
    try:
        model = get_model('url')
        if not model:
            raise HTTPException(status_code=503, detail="URL ML model not loaded")

        url_result = analyze_url(request.url, model)

        # Check crowd database for domain
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(request.url if '://' in request.url else 'http://' + request.url)
            domain = parsed.netloc
            crowd_check = check_crowd_database(domain=domain)
        except Exception:
            crowd_check = {"found": False, "report_count": 0}

        risk_result = calculate_risk_score(url_analysis=url_result)

        result = {
            "type": "url_analysis",
            "url": request.url,
            "is_safe": url_result['is_safe'],
            "verdict": url_result['verdict'],
            "safety_score": url_result['safety_score'],
            "risk_score": risk_result['overall_risk_score'],
            "risk_level": risk_result['risk_level'],
            "confidence": url_result['confidence'],
            "flags": url_result['flags'],
            "explanation": url_result['explanation'],
            "domain_info": url_result['domain_info'],
            "crowd_database": crowd_check,
            "recommendation": risk_result['recommendation'],
            "timestamp": datetime.utcnow().isoformat()
        }

        save_analysis("analysis_history", {
            **result,
            "is_scam": not url_result['is_safe'],
            "scam_type": "URL/Phishing" if not url_result['is_safe'] else None
        })

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"URL analysis failed: {str(e)}")


@router.post("/email")
async def analyze_email(request: EmailAnalysisRequest):
    """Analyze email for scam/phishing detection."""
    try:
        model = get_model('text')
        if not model:
            raise HTTPException(status_code=503, detail="ML model not loaded")

        # Combine subject and body for analysis
        full_content = f"Subject: {request.subject}\n\n{request.body}"
        text_result = analyze_text(full_content, model)

        # Extra email-specific checks
        email_flags = []
        email_risk_boost = 0

        # Check subject line for urgency
        subject_lower = request.subject.lower()
        urgent_subject_words = ['urgent', 'action required', 'verify', 'suspended', 'winner', 'selected', 'claim']
        for word in urgent_subject_words:
            if word in subject_lower:
                email_flags.append(f"Suspicious subject keyword: '{word}'")
                email_risk_boost += 10

        # Check sender email
        if request.sender_email:
            sender_lower = request.sender_email.lower()
            free_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            suspicious_domains = ['.tk', '.ml', '.xyz', '.top', '.club']

            if any(request.subject.lower().count(brand) > 0 for brand in ['paypal', 'amazon', 'apple', 'microsoft', 'irs', 'bank']):
                if any(sender_lower.endswith(d) for d in free_domains):
                    email_flags.append("Official brand using free email domain — likely spoofing")
                    email_risk_boost += 30

            if any(sender_lower.endswith(d) for d in suspicious_domains):
                email_flags.append(f"Suspicious sender domain")
                email_risk_boost += 25

        # Reply-to mismatch
        if request.reply_to and request.sender_email:
            if request.reply_to.split('@')[1] != request.sender_email.split('@')[1] if '@' in request.reply_to and '@' in request.sender_email else False:
                email_flags.append("Reply-to domain differs from sender domain")
                email_risk_boost += 20

        # Attachments from unknown
        if request.has_attachments:
            email_flags.append("Email contains attachments — verify before opening")
            email_risk_boost += 10

        # URL analysis for links in body
        import re
        urls_in_body = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+', request.body)
        url_results = []
        url_model = get_model('url')
        for url in urls_in_body[:5]:  # Check first 5 URLs
            url_r = analyze_url(url, url_model)
            url_results.append(url_r)
            if not url_r['is_safe']:
                email_risk_boost += 15
                email_flags.append(f"Suspicious link found: {url[:50]}...")

        # Calculate composite risk
        adjusted_text_risk = min(100, text_result['risk_score'] + email_risk_boost)
        modified_text_result = {**text_result, 'risk_score': adjusted_text_risk}
        risk_result = calculate_risk_score(text_analysis=modified_text_result)

        result = {
            "type": "email_analysis",
            "subject": request.subject,
            "sender_email": request.sender_email,
            "is_scam": text_result['is_scam'] or email_risk_boost > 30,
            "confidence": text_result['confidence'],
            "scam_type": text_result.get('scam_type') or ("Email Phishing" if email_risk_boost > 20 else None),
            "risk_score": risk_result['overall_risk_score'],
            "risk_level": risk_result['risk_level'],
            "explanation": text_result['explanation'] + email_flags,
            "email_specific_flags": email_flags,
            "urls_found": len(urls_in_body),
            "suspicious_urls": [r for r in url_results if not r['is_safe']],
            "recommendation": risk_result['recommendation'],
            "timestamp": datetime.utcnow().isoformat()
        }

        save_analysis("analysis_history", {
            **result,
            "input": full_content[:300]
        })

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Email analysis failed: {str(e)}")


@router.post("/voice")
async def analyze_voice(request: VoiceTranscriptRequest):
    """Analyze voice call transcript for scam detection."""
    try:
        voice_result = analyze_voice_transcript(request.transcript)

        behavioral_result = None
        if request.caller_id:
            crowd_check = check_crowd_database(phone=request.caller_id)
            if crowd_check.get('found'):
                behavioral_result = {
                    'behavioral_risk_score': crowd_check['report_count'] * 15,
                    'risk_factors': [f"Number reported {crowd_check['report_count']} time(s)"]
                }

        risk_result = calculate_risk_score(
            voice_analysis=voice_result,
            behavioral_analysis=behavioral_result
        )

        result = {
            "type": "voice_analysis",
            "transcript_preview": request.transcript[:200] + "..." if len(request.transcript) > 200 else request.transcript,
            "caller_id": request.caller_id,
            "call_duration": request.call_duration,
            "is_scam": voice_result['is_scam'],
            "confidence": voice_result['confidence'],
            "scam_type": voice_result.get('scam_type'),
            "risk_score": risk_result['overall_risk_score'],
            "risk_level": risk_result['risk_level'],
            "flagged_phrases": voice_result['flagged_phrases'],
            "tone_analysis": voice_result['tone_analysis'],
            "explanation": voice_result['explanation'],
            "recommendation": risk_result['recommendation'],
            "timestamp": datetime.utcnow().isoformat()
        }

        save_analysis("analysis_history", {
            **result,
            "input": request.transcript[:300],
            "is_scam": voice_result['is_scam'],
        })

        return result

    except Exception as e:
        logger.error(f"Voice analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Voice analysis failed: {str(e)}")


@router.post("/voice/audio")
async def analyze_voice_audio(file: UploadFile = File(...)):
    """Analyze uploaded audio file for voice scam detection."""
    try:
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be audio format")

        audio_data = await file.read()
        audio_result = analyze_speech_audio(audio_data)

        return {
            "type": "audio_analysis",
            "filename": file.filename,
            "file_size": len(audio_data),
            "transcript": audio_result['transcript'],
            "transcription_confidence": audio_result['transcription_confidence'],
            "analysis": audio_result['analysis'],
            "note": "Integrate Google Speech-to-Text or OpenAI Whisper for production transcription",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio analysis failed: {str(e)}")
