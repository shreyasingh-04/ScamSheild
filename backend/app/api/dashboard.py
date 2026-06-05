from fastapi import APIRouter
from datetime import datetime
import logging
from app.utils.firebase import get_dashboard_stats, get_analysis_history

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats")
async def get_stats():
    """Get dashboard statistics."""
    try:
        stats = get_dashboard_stats()
        return {
            **stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return {
            "total_analyzed": 0,
            "scams_detected": 0,
            "safe_messages": 0,
            "detection_rate": 0,
            "crowd_reports": 0,
            "scam_types": {},
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/history")
async def get_history(limit: int = 20):
    """Get recent analysis history."""
    try:
        history = get_analysis_history("analysis_history", limit=limit)
        return {
            "total": len(history),
            "items": history
        }
    except Exception as e:
        logger.error(f"History error: {e}")
        return {"total": 0, "items": []}


@router.get("/trends")
async def get_trends():
    """Get scam trends data for charts."""
    from app.utils.firebase import _in_memory_db
    analyses = _in_memory_db.get("analysis_history", [])

    # Mock trends data for demo
    from datetime import timedelta
    today = datetime.utcnow()
    trend_data = []
    for i in range(7, -1, -1):
        date = today - timedelta(days=i)
        day_analyses = [a for a in analyses if a.get('created_at', '').startswith(date.strftime('%Y-%m-%d'))]
        trend_data.append({
            "date": date.strftime('%Y-%m-%d'),
            "total": len(day_analyses),
            "scams": sum(1 for a in day_analyses if a.get('is_scam')),
            "safe": sum(1 for a in day_analyses if not a.get('is_scam'))
        })

    scam_type_dist = {
        "Phishing Attack": 28,
        "Financial Fraud": 22,
        "Government Impersonation": 18,
        "Romance Scam": 12,
        "Job Scam": 10,
        "Prize/Lottery": 6,
        "Tech Support": 4,
    }

    return {
        "weekly_trend": trend_data,
        "scam_type_distribution": scam_type_dist,
        "top_risk_countries": ["Nigeria", "India", "Romania", "China", "Russia"],
        "peak_scam_hours": [2, 3, 10, 11, 14, 15, 20, 21],
    }
