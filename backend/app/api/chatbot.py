from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import logging
import re

from app.ml.text_analyzer import analyze_text, extract_suspicious_keywords
from app.ml.url_analyzer import analyze_url
from app.ml.model_loader import get_model

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []
    user_id: Optional[str] = None


def extract_content_from_message(message: str) -> Dict:
    """Extract URLs and text content from user message."""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, message)

    # Check if message contains a forwarded text
    contains_quoted = '"' in message or "'" in message or message.lower().startswith("is this")

    return {
        "urls": urls,
        "has_urls": len(urls) > 0,
        "seems_like_forwarded_content": contains_quoted,
        "direct_question": any(q in message.lower() for q in ["is this", "safe?", "scam?", "legit?", "real?", "should i"])
    }


def build_scam_explanation(analysis_result: Dict) -> str:
    """Build a human-readable explanation from analysis results."""
    if analysis_result.get('is_scam'):
        confidence = analysis_result.get('confidence', 0)
        scam_type = analysis_result.get('scam_type', 'Unknown')
        explanation_points = analysis_result.get('explanation', [])
        keywords = analysis_result.get('keyword_analysis', {})

        response = f"🚨 **This appears to be a SCAM** (Confidence: {confidence:.0f}%)\n\n"
        if scam_type:
            response += f"**Type:** {scam_type}\n\n"
        response += "**Why it's suspicious:**\n"
        for point in explanation_points[:5]:
            response += f"• {point}\n"

        if keywords:
            flat_keywords = []
            for kw_list in keywords.values():
                flat_keywords.extend(kw_list[:2])
            if flat_keywords:
                response += f"\n**Red flag words:** {', '.join(flat_keywords[:8])}\n"

        response += "\n**Recommendation:** Do NOT click any links, provide personal information, or send money."
    else:
        response = f"✅ **This appears to be SAFE** "
        confidence = 100 - analysis_result.get('confidence', 50)
        response += f"(Safe confidence: {confidence:.0f}%)\n\n"
        response += "No significant scam indicators were detected in this message.\n"
        response += "However, always stay cautious and verify unexpected requests independently."

    return response


def generate_rule_based_response(user_message: str) -> str:
    """Generate helpful responses using rule-based logic + ML analysis."""
    msg_lower = user_message.lower()

    # Check if user is asking about a specific message/URL
    content = extract_content_from_message(user_message)

    # If URLs found, analyze them
    if content['has_urls']:
        url_model = get_model('url')
        responses = []
        for url in content['urls'][:3]:
            url_result = analyze_url(url, url_model)
            if not url_result['is_safe']:
                responses.append(f"⚠️ **Dangerous URL detected:** `{url}`\n"
                               f"Safety Score: {url_result['safety_score']:.0f}/100\n"
                               f"Issues: {', '.join(url_result['flags'][:3])}\n"
                               f"**Do NOT visit this link!**")
            else:
                responses.append(f"✅ **URL appears safe:** `{url}`\n"
                               f"Safety Score: {url_result['safety_score']:.0f}/100")
        return "\n\n".join(responses)

    # If seems like forwarded scam content
    if content['seems_like_forwarded_content'] or content['direct_question']:
        # Extract the actual content to analyze
        text_to_analyze = user_message
        for prefix in ["is this safe?", "is this a scam?", "check this:", "analyze:", "is this legit?"]:
            if msg_lower.startswith(prefix):
                text_to_analyze = user_message[len(prefix):].strip()
                break

        model = get_model('text')
        if model and len(text_to_analyze) > 10:
            result = analyze_text(text_to_analyze, model)
            return build_scam_explanation(result)

    # General scam education responses
    if any(w in msg_lower for w in ['what is', 'how to', 'explain', 'tell me about']):
        if 'phishing' in msg_lower:
            return ("🎣 **Phishing** is when scammers impersonate trusted organizations (banks, PayPal, Amazon) "
                    "to steal your credentials.\n\n**Signs:**\n• Urgent requests to 'verify' your account\n"
                    "• Links that look similar but aren't official (e.g., amaz0n.com)\n"
                    "• Generic greetings like 'Dear Customer'\n\n**Protection:** Always go directly to the official website.")

        if 'romance scam' in msg_lower:
            return ("💔 **Romance scams** involve fake online relationships to extract money.\n\n"
                    "**Red flags:**\n• Claims to be overseas (military, oil rig, doctor)\n"
                    "• Asks for money for emergencies\n• Never meets in person or via video\n"
                    "• Moves very fast emotionally\n\n**Rule:** Never send money to someone you haven't met in person.")

        if 'irs' in msg_lower or 'tax scam' in msg_lower:
            return ("📋 **IRS/Tax Scams** involve fake government agents threatening arrest for unpaid taxes.\n\n"
                    "**Know this:** The IRS *never*:\n• Calls to demand immediate payment\n"
                    "• Threatens to send police\n• Requires gift cards or wire transfers\n\n"
                    "**If called:** Hang up immediately. Report to IRS.gov/phishing")

    # Tips and general help
    if any(w in msg_lower for w in ['tips', 'advice', 'protect', 'safe', 'how do i']):
        return ("🛡️ **Top Scam Protection Tips:**\n\n"
                "1. **Never give personal info** to unsolicited callers/emailers\n"
                "2. **Verify independently** — call official numbers from official websites\n"
                "3. **No legitimate company** asks for gift cards as payment\n"
                "4. **Urgency = red flag** — scammers rush you to prevent thinking clearly\n"
                "5. **Check URLs carefully** before clicking — look for misspellings\n"
                "6. **Enable 2FA** on all important accounts\n"
                "7. **When in doubt, don't** — hang up, delete, ignore\n\n"
                "You can paste any suspicious message or URL here and I'll analyze it! 🔍")

    if any(w in msg_lower for w in ['hello', 'hi', 'hey', 'help', 'start']):
        return ("👋 **Hello! I'm ScamShield AI Assistant.**\n\n"
                "I can help you:\n"
                "• 🔍 **Analyze suspicious messages** — just paste them here\n"
                "• 🌐 **Check URLs** — paste any link to verify safety\n"
                "• 📚 **Learn about scam types** — ask me about phishing, romance scams, IRS scams, etc.\n"
                "• 🛡️ **Get protection tips** — ask for advice\n\n"
                "What would you like to check today?")

    # Default: analyze the message itself
    model = get_model('text')
    if model and len(user_message) > 15:
        result = analyze_text(user_message, model)
        if result.get('is_scam'):
            return build_scam_explanation(result)

    return ("I'm here to help you detect scams! You can:\n"
            "• **Paste a suspicious message** for analysis\n"
            "• **Share a URL** to check if it's safe\n"
            "• **Ask about scam types** (phishing, romance scams, etc.)\n"
            "• **Request protection tips**\n\n"
            "What would you like to know? 🔍")


async def call_openai_chatbot(user_message: str, history: List[Dict], context: str = "") -> str:
    """Call OpenAI API for intelligent chatbot response."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        import httpx

        system_prompt = """You are ScamShield AI, an expert cybersecurity assistant specializing in scam detection and prevention. 

Your role:
1. Analyze suspicious messages, emails, SMS, and URLs for scam indicators
2. Explain why something is or isn't a scam in simple, clear language
3. Educate users about different scam types
4. Provide actionable protection advice

When analyzing content:
- Be specific about RED FLAGS you identify
- Explain the scam technique being used
- Give a clear SAFE/SUSPICIOUS/SCAM verdict
- Suggest what the user should do

Always be empathetic, clear, and non-technical. Many users may be elderly or not tech-savvy.
""" + (f"\n\nAdditional context from ML analysis:\n{context}" if context else "")

        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-10:]:  # Last 10 messages
            messages.append(h)
        messages.append({"role": "user", "content": user_message})

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "max_tokens": 800,
                    "temperature": 0.7
                }
            )
            data = response.json()
            return data['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None


@router.post("/ask")
async def chatbot_ask(request: ChatRequest):
    """AI Chatbot for scam-related queries."""
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # First, do ML analysis for context
        model = get_model('text')
        ml_context = ""
        if model and len(request.message) > 20:
            result = analyze_text(request.message, model)
            if result.get('is_scam'):
                ml_context = (f"ML Analysis detected potential scam: {result.get('scam_type', 'Unknown type')}, "
                             f"confidence {result.get('confidence', 0):.0f}%, "
                             f"keywords: {list(result.get('keyword_analysis', {}).keys())}")

        # Try OpenAI first, fall back to rule-based
        response_text = await call_openai_chatbot(
            request.message,
            request.conversation_history or [],
            ml_context
        )

        if not response_text:
            response_text = generate_rule_based_response(request.message)
            source = "rule_based"
        else:
            source = "openai_gpt4"

        return {
            "response": response_text,
            "source": source,
            "ml_context": ml_context if ml_context else None,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chatbot error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")
