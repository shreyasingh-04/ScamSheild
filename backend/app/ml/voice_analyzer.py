import re
from typing import Dict, List, Any
import logging
import numpy as np

logger = logging.getLogger(__name__)

VOICE_SCAM_PATTERNS = {
    "urgency_phrases": [
        "your account will be suspended",
        "you must act now",
        "this is your final warning",
        "you are under investigation",
        "do not hang up",
        "stay on the line",
        "this call is being recorded",
        "press 1 immediately",
        "your social security",
        "arrest warrant",
        "irs",
        "federal agent",
    ],
    "financial_pressure": [
        "gift card",
        "wire transfer",
        "bitcoin",
        "western union",
        "cash only",
        "money order",
        "send money",
        "bank account number",
        "routing number",
        "credit card number",
    ],
    "fear_tactics": [
        "arrested",
        "deported",
        "lawsuit",
        "criminal charges",
        "court appearance",
        "jail",
        "prison",
        "police",
        "federal",
        "government",
    ],
    "fake_offers": [
        "congratulations you won",
        "free vacation",
        "selected for",
        "special offer",
        "limited time",
        "no obligation",
        "just pay shipping",
        "risk free",
        "100 percent guaranteed",
    ]
}

VOICE_TONE_INDICATORS = {
    "high_urgency": ["immediately", "now", "urgent", "emergency", "critical", "final"],
    "threats": ["arrest", "suspend", "deport", "shut down", "legal action"],
    "pressure": ["don't tell", "secret", "confidential", "don't hang up", "stay on line"],
    "rewards": ["won", "selected", "prize", "reward", "bonus", "free"],
}


def analyze_voice_transcript(transcript: str) -> Dict[str, Any]:
    """Analyze a voice call transcript for scam indicators."""
    if not transcript or len(transcript.strip()) < 10:
        return {
            "is_scam": False,
            "confidence": 0,
            "risk_score": 0,
            "scam_type": None,
            "tone_analysis": {},
            "flagged_phrases": [],
            "explanation": ["Transcript too short to analyze"]
        }

    transcript_lower = transcript.lower()
    flagged_phrases = []
    risk_score = 0
    explanation = []

    # Check each pattern category
    category_scores = {}
    for category, patterns in VOICE_SCAM_PATTERNS.items():
        found = [p for p in patterns if p in transcript_lower]
        category_scores[category] = len(found)
        flagged_phrases.extend(found)
        if found:
            risk_score += len(found) * 10
            explanation.append(f"{category.replace('_', ' ').title()}: {', '.join(found[:3])}")

    # Tone analysis
    tone_analysis = {}
    for tone, indicators in VOICE_TONE_INDICATORS.items():
        found = [i for i in indicators if i in transcript_lower]
        tone_analysis[tone] = {
            "detected": len(found) > 0,
            "indicators": found
        }
        if found:
            risk_score += len(found) * 5

    # Word density analysis
    words = transcript_lower.split()
    word_count = len(words)

    # Exclamation and caps in transcript
    exclamation_count = transcript.count('!')
    if exclamation_count > 3:
        risk_score += 10
        explanation.append(f"High emotional intensity in speech ({exclamation_count} exclamations)")

    # Caps ratio (for transcribed ALL CAPS words)
    caps_words = [w for w in words if w.isupper() and len(w) > 2]
    if len(caps_words) > 3:
        risk_score += 10
        explanation.append(f"Shouting/emphasis detected in speech")

    # Determine scam type
    scam_type = None
    if category_scores.get('urgency_phrases', 0) > 2:
        if 'irs' in transcript_lower or 'tax' in transcript_lower:
            scam_type = "IRS/Tax Scam"
        elif 'social security' in transcript_lower:
            scam_type = "Social Security Scam"
        elif 'arrest' in transcript_lower or 'police' in transcript_lower:
            scam_type = "Government Authority Scam"

    if not scam_type:
        if category_scores.get('financial_pressure', 0) > 1:
            scam_type = "Financial Fraud"
        elif category_scores.get('fake_offers', 0) > 1:
            scam_type = "Prize/Lottery Scam"
        elif category_scores.get('fear_tactics', 0) > 1:
            scam_type = "Threat Scam"

    risk_score = min(100, risk_score)
    is_scam = risk_score > 30

    if not explanation:
        explanation.append("Voice content appears safe based on pattern analysis")

    return {
        "is_scam": is_scam,
        "confidence": round(min(95, risk_score + 20) if is_scam else max(5, 100 - risk_score), 1),
        "risk_score": risk_score,
        "scam_type": scam_type,
        "tone_analysis": tone_analysis,
        "flagged_phrases": list(set(flagged_phrases))[:10],
        "explanation": explanation,
        "transcript_stats": {
            "word_count": word_count,
            "category_scores": category_scores,
        }
    }


def analyze_speech_audio(audio_data: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
    """
    Analyze audio data for voice scam detection.
    In production, integrate with Google Speech-to-Text or Whisper API.
    Returns transcript + analysis.
    """
    # Placeholder for speech-to-text integration
    # In production: use openai.Audio.transcribe() or Google STT
    mock_transcript = "[Audio transcription requires Google Speech-to-Text or OpenAI Whisper API integration]"

    return {
        "transcript": mock_transcript,
        "transcription_confidence": 0.0,
        "analysis": analyze_voice_transcript(mock_transcript),
        "audio_features": {
            "duration_seconds": len(audio_data) / (sample_rate * 2) if audio_data else 0,
            "sample_rate": sample_rate,
        }
    }


def detect_deepfake_voice_indicators(transcript: str, audio_metadata: Dict = None) -> Dict[str, Any]:
    """
    Detect potential deepfake voice indicators.
    In production, integrate with dedicated deepfake detection models.
    """
    indicators = []
    risk_score = 0

    # Text-based indicators of cloned voice patterns
    if audio_metadata:
        # Check for unnatural pauses or inconsistencies
        if audio_metadata.get('unusual_pauses', False):
            indicators.append("Unusual pause patterns detected")
            risk_score += 20

        if audio_metadata.get('pitch_inconsistency', False):
            indicators.append("Inconsistent pitch variations")
            risk_score += 25

        if audio_metadata.get('background_noise_absent', False):
            indicators.append("Suspiciously clean audio — may indicate synthesis")
            risk_score += 15

    return {
        "deepfake_risk": risk_score,
        "indicators": indicators,
        "is_potentially_deepfake": risk_score > 30,
        "note": "Full deepfake detection requires specialized ML models (ElevenLabs detector, etc.)"
    }
