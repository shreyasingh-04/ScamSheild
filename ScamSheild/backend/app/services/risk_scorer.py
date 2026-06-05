from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_risk_score(
    text_analysis: Optional[Dict] = None,
    url_analysis: Optional[Dict] = None,
    voice_analysis: Optional[Dict] = None,
    behavioral_analysis: Optional[Dict] = None,
    sender_info: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Calculate a composite risk score (0-100) from multiple analysis sources.
    """
    weighted_scores = []
    contributing_factors = []
    risk_breakdown = {}

    # Text analysis (weight: 35%)
    if text_analysis:
        score = text_analysis.get('risk_score', 0)
        weighted = score * 0.35
        weighted_scores.append(weighted)
        risk_breakdown['text_analysis'] = score
        if score > 50:
            contributing_factors.append(f"Suspicious text content (score: {score})")

    # URL analysis (weight: 30%)
    if url_analysis:
        score = url_analysis.get('risk_score', 0)
        weighted = score * 0.30
        weighted_scores.append(weighted)
        risk_breakdown['url_analysis'] = score
        if score > 40:
            contributing_factors.append(f"Risky URL detected (score: {score})")

    # Voice analysis (weight: 20%)
    if voice_analysis:
        score = voice_analysis.get('risk_score', 0)
        weighted = score * 0.20
        weighted_scores.append(weighted)
        risk_breakdown['voice_analysis'] = score
        if score > 40:
            contributing_factors.append(f"Suspicious voice patterns (score: {score})")

    # Behavioral analysis (weight: 15%)
    if behavioral_analysis:
        score = behavioral_analysis.get('behavioral_risk_score', 0)
        weighted = score * 0.15
        weighted_scores.append(weighted)
        risk_breakdown['behavioral_analysis'] = score
        if score > 30:
            contributing_factors.extend(behavioral_analysis.get('risk_factors', []))

    # Sender info adjustments
    sender_modifier = 0
    if sender_info:
        if sender_info.get('is_unknown', False):
            sender_modifier += 10
            contributing_factors.append("Unknown sender")
        if sender_info.get('is_international', False):
            sender_modifier += 5
            contributing_factors.append("International source")
        if sender_info.get('report_count', 0) > 0:
            reports = sender_info['report_count']
            sender_modifier += min(reports * 10, 30)
            contributing_factors.append(f"Sender reported {reports} time(s) by community")

    # Calculate final score
    if weighted_scores:
        # Normalize by number of components analyzed
        base_score = sum(weighted_scores) / max(len(weighted_scores) * 0.35, 0.35)
        final_score = min(100, base_score + sender_modifier)
    else:
        final_score = sender_modifier

    # Determine risk level
    if final_score >= 75:
        risk_level = "CRITICAL"
        risk_color = "#FF0000"
        recommendation = "Do NOT engage. Block this sender immediately."
    elif final_score >= 50:
        risk_level = "HIGH"
        risk_color = "#FF6B00"
        recommendation = "Treat with extreme caution. Very likely a scam."
    elif final_score >= 30:
        risk_level = "MEDIUM"
        risk_color = "#FFD700"
        recommendation = "Exercise caution. Verify independently before responding."
    elif final_score >= 10:
        risk_level = "LOW"
        risk_color = "#90EE90"
        recommendation = "Appears relatively safe, but stay vigilant."
    else:
        risk_level = "SAFE"
        risk_color = "#00CC00"
        recommendation = "No significant scam indicators detected."

    return {
        "overall_risk_score": round(final_score, 1),
        "risk_level": risk_level,
        "risk_color": risk_color,
        "recommendation": recommendation,
        "contributing_factors": contributing_factors,
        "risk_breakdown": risk_breakdown,
        "analysis_count": len(weighted_scores),
    }


def get_risk_level_info(score: float) -> Dict[str, str]:
    """Get risk level details for a given score."""
    if score >= 75:
        return {"level": "CRITICAL", "color": "#FF0000", "icon": "🚨"}
    elif score >= 50:
        return {"level": "HIGH", "color": "#FF6B00", "icon": "⚠️"}
    elif score >= 30:
        return {"level": "MEDIUM", "color": "#FFD700", "icon": "⚡"}
    elif score >= 10:
        return {"level": "LOW", "color": "#90EE90", "icon": "ℹ️"}
    else:
        return {"level": "SAFE", "color": "#00CC00", "icon": "✅"}
