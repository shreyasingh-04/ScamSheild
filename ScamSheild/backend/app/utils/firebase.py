import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# In-memory storage as Firebase fallback for development
_in_memory_db = {
    "scam_reports": [],
    "analysis_history": [],
    "crowd_reports": [],
    "user_stats": {},
}

_firebase_initialized = False


def init_firebase():
    """Initialize Firebase connection."""
    global _firebase_initialized

    firebase_creds = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if not firebase_creds:
        logger.warning("⚠️ FIREBASE_CREDENTIALS_PATH not set. Using in-memory storage for development.")
        _firebase_initialized = False
        return

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)

        _firebase_initialized = True
        logger.info("✅ Firebase Firestore initialized successfully")
    except ImportError:
        logger.warning("firebase-admin not installed. Using in-memory storage.")
        _firebase_initialized = False
    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e}. Using in-memory storage.")
        _firebase_initialized = False


def save_analysis(collection: str, data: Dict[str, Any]) -> str:
    """Save analysis result to Firebase or in-memory DB."""
    doc_id = str(uuid.uuid4())
    data['id'] = doc_id
    data['created_at'] = datetime.utcnow().isoformat()

    if _firebase_initialized:
        try:
            from firebase_admin import firestore
            db = firestore.client()
            db.collection(collection).document(doc_id).set(data)
            return doc_id
        except Exception as e:
            logger.error(f"Firebase save failed: {e}")

    # Fallback to in-memory
    if collection not in _in_memory_db:
        _in_memory_db[collection] = []
    _in_memory_db[collection].append(data)
    return doc_id


def get_analysis_history(collection: str, limit: int = 50) -> List[Dict]:
    """Get analysis history."""
    if _firebase_initialized:
        try:
            from firebase_admin import firestore
            db = firestore.client()
            docs = db.collection(collection).order_by('created_at', direction='DESCENDING').limit(limit).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Firebase get failed: {e}")

    data = _in_memory_db.get(collection, [])
    return sorted(data, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]


def save_crowd_report(report_data: Dict[str, Any]) -> str:
    """Save a crowd-sourced scam report."""
    return save_analysis("crowd_reports", report_data)


def get_crowd_reports(limit: int = 100) -> List[Dict]:
    """Get crowd-sourced scam reports."""
    return get_analysis_history("crowd_reports", limit)


def check_crowd_database(phone: str = None, domain: str = None) -> Dict[str, Any]:
    """Check if phone/domain is in crowd-sourced scam database."""
    reports = get_crowd_reports()
    matches = []

    for report in reports:
        if phone and report.get('phone_number') == phone:
            matches.append(report)
        if domain and domain in report.get('url', ''):
            matches.append(report)

    return {
        "found": len(matches) > 0,
        "report_count": len(matches),
        "reports": matches[:5],
        "is_known_scam": len(matches) >= 3
    }


def get_dashboard_stats() -> Dict[str, Any]:
    """Get aggregated statistics for dashboard."""
    all_analyses = _in_memory_db.get("analysis_history", [])
    crowd_reports = _in_memory_db.get("crowd_reports", [])

    total = len(all_analyses)
    scams = sum(1 for a in all_analyses if a.get('is_scam', False))
    safe = total - scams

    scam_types = {}
    for a in all_analyses:
        st = a.get('scam_type')
        if st:
            scam_types[st] = scam_types.get(st, 0) + 1

    return {
        "total_analyzed": total,
        "scams_detected": scams,
        "safe_messages": safe,
        "detection_rate": round((scams / total * 100) if total > 0 else 0, 1),
        "crowd_reports": len(crowd_reports),
        "scam_types": dict(sorted(scam_types.items(), key=lambda x: x[1], reverse=True)[:10]),
        "recent_analyses": all_analyses[-10:] if all_analyses else [],
    }
