import re
import numpy as np
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

SCAM_KEYWORDS = {
    "urgency": ["urgent", "immediately", "asap", "right now", "today only", "expires", "deadline", "final notice", "last chance", "act now", "hurry"],
    "financial": ["bank account", "credit card", "wire transfer", "western union", "gift card", "bitcoin", "crypto", "investment", "profit", "returns", "lottery", "won", "winner", "prize", "claim", "refund"],
    "threat": ["arrest", "lawsuit", "legal action", "suspended", "blocked", "compromised", "virus", "hack", "breach", "penalty", "fine", "court"],
    "personal_info": ["ssn", "social security", "password", "pin", "account number", "verify identity", "confirm details", "personal information"],
    "impersonation": ["irs", "fbi", "microsoft", "amazon", "apple", "paypal", "netflix", "bank of america", "chase", "wells fargo", "government"],
    "unrealistic": ["guaranteed", "100%", "no risk", "free money", "make money fast", "work from home", "no experience", "unlimited", "million dollars"],
    "romance": ["fell in love", "beautiful profile", "need money", "send money", "flight ticket", "meet you", "lonely", "widow", "offshore"],
}

SUSPICIOUS_PATTERNS = [
    r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Phone numbers
    r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',  # Emails
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
    r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # Dollar amounts
    r'\b(?:click|tap|visit|go to|open|download)\s+(?:here|link|now|this)\b',  # CTAs
]


def extract_text_features(text: str) -> Dict[str, Any]:
    """Extract features from text for scam detection."""
    text_lower = text.lower()
    features = {}

    # Keyword category scores
    keyword_hits = {}
    total_keyword_score = 0
    for category, keywords in SCAM_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in text_lower]
        keyword_hits[category] = hits
        total_keyword_score += len(hits)

    features['keyword_hits'] = keyword_hits
    features['total_keyword_score'] = total_keyword_score

    # Pattern detection
    pattern_matches = {}
    for i, pattern in enumerate(SUSPICIOUS_PATTERNS):
        matches = re.findall(pattern, text, re.IGNORECASE)
        pattern_matches[f'pattern_{i}'] = len(matches)

    features['pattern_matches'] = pattern_matches

    # Text characteristics
    features['exclamation_count'] = text.count('!')
    features['caps_ratio'] = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    features['text_length'] = len(text)
    features['word_count'] = len(text.split())
    features['url_count'] = len(re.findall(r'http[s]?://', text))
    features['number_count'] = len(re.findall(r'\d+', text))

    # Urgency indicators
    urgency_words = ["urgent", "immediately", "asap", "now", "today", "expires", "deadline", "hurry"]
    features['urgency_score'] = sum(1 for w in urgency_words if w in text_lower)

    return features


def analyze_text(text: str, model) -> Dict[str, Any]:
    """Analyze text for scam indicators."""
    if not text or len(text.strip()) < 5:
        return {
            "is_scam": False,
            "confidence": 0.0,
            "risk_score": 0,
            "explanation": ["Text too short to analyze"],
            "keyword_analysis": {},
            "scam_type": None
        }

    # Get ML prediction
    try:
        proba = model.predict_proba([text])[0]
        scam_probability = float(proba[1])
        is_scam = scam_probability > 0.5
    except Exception as e:
        logger.warning(f"ML prediction failed: {e}")
        scam_probability = 0.0
        is_scam = False

    # Feature extraction
    features = extract_text_features(text)

    # Rule-based boosting
    rule_boost = 0
    explanation = []

    for category, hits in features['keyword_hits'].items():
        if hits:
            rule_boost += len(hits) * 0.05
            explanation.append(f"Contains {category} keywords: {', '.join(hits[:3])}")

    if features['exclamation_count'] > 3:
        rule_boost += 0.1
        explanation.append(f"Excessive exclamation marks ({features['exclamation_count']})")

    if features['caps_ratio'] > 0.3:
        rule_boost += 0.1
        explanation.append(f"High proportion of capital letters ({features['caps_ratio']:.0%})")

    if features['url_count'] > 0:
        rule_boost += 0.05
        explanation.append(f"Contains {features['url_count']} URL(s)")

    if features['urgency_score'] > 2:
        rule_boost += 0.1
        explanation.append(f"Multiple urgency indicators detected")

    # Combine ML + rule-based score
    final_score = min(1.0, scam_probability + (rule_boost * 0.5))
    risk_score = int(final_score * 100)
    is_scam = final_score > 0.45

    # Determine scam type
    scam_type = determine_scam_type(features, text.lower())

    if not explanation and is_scam:
        explanation.append("ML model detected suspicious patterns in the text")
    elif not explanation:
        explanation.append("Text appears safe based on content analysis")

    return {
        "is_scam": is_scam,
        "confidence": round(final_score * 100, 1),
        "risk_score": risk_score,
        "explanation": explanation,
        "keyword_analysis": {
            cat: hits for cat, hits in features['keyword_hits'].items() if hits
        },
        "scam_type": scam_type,
        "text_features": {
            "word_count": features['word_count'],
            "urgency_score": features['urgency_score'],
            "caps_ratio": round(features['caps_ratio'] * 100, 1),
            "url_count": features['url_count'],
        }
    }


def determine_scam_type(features: Dict, text_lower: str) -> str | None:
    """Determine the type of scam based on features."""
    keyword_hits = features.get('keyword_hits', {})

    if keyword_hits.get('romance'):
        return "Romance Scam"
    elif keyword_hits.get('threat') and keyword_hits.get('impersonation'):
        return "Government/Authority Impersonation"
    elif keyword_hits.get('financial') and keyword_hits.get('unrealistic'):
        return "Investment/Financial Fraud"
    elif keyword_hits.get('urgency') and keyword_hits.get('personal_info'):
        return "Phishing Attack"
    elif "job" in text_lower or "work from home" in text_lower or "earn" in text_lower:
        return "Job Scam"
    elif keyword_hits.get('financial') and "lottery" in text_lower:
        return "Lottery/Prize Scam"
    elif keyword_hits.get('threat'):
        return "Threat/Extortion Scam"
    elif keyword_hits.get('impersonation'):
        return "Impersonation Scam"
    elif features.get('total_keyword_score', 0) > 3:
        return "General Scam"

    return None


def extract_suspicious_keywords(text: str) -> List[str]:
    """Extract all suspicious keywords found in text."""
    text_lower = text.lower()
    found = []
    for category, keywords in SCAM_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                found.append(kw)
    return list(set(found))


def calculate_behavioral_risk(
    message_frequency: int,
    unusual_timing: bool,
    unknown_sender: bool,
    international_source: bool,
    previous_reports: int
) -> Dict[str, Any]:
    """Calculate behavioral anomaly risk score."""
    risk_factors = []
    risk_score = 0

    if message_frequency > 10:
        risk_score += 20
        risk_factors.append(f"High message frequency: {message_frequency} messages")

    if unusual_timing:
        risk_score += 15
        risk_factors.append("Messages sent at unusual hours (2AM - 6AM)")

    if unknown_sender:
        risk_score += 25
        risk_factors.append("Unknown sender with no prior communication history")

    if international_source:
        risk_score += 20
        risk_factors.append("International source detected")

    if previous_reports > 0:
        risk_score += min(previous_reports * 10, 40)
        risk_factors.append(f"Reported {previous_reports} time(s) by other users")

    return {
        "behavioral_risk_score": min(risk_score, 100),
        "risk_factors": risk_factors,
        "is_anomalous": risk_score > 30
    }
