from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

from app.utils.firebase import save_crowd_report, get_crowd_reports, check_crowd_database

router = APIRouter()
logger = logging.getLogger(__name__)


class ScamReport(BaseModel):
    report_type: str  # phone, email, url, message
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    url: Optional[str] = None
    message_content: Optional[str] = None
    scam_type: Optional[str] = None
    description: str
    reporter_location: Optional[str] = None
    financial_loss: Optional[float] = None
    currency: Optional[str] = "USD"


class CheckRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    domain: Optional[str] = None


@router.post("/scam")
async def report_scam(report: ScamReport):
    """Submit a crowd-sourced scam report."""
    try:
        report_data = {
            "report_type": report.report_type,
            "phone_number": report.phone_number,
            "email_address": report.email_address,
            "url": report.url,
            "message_content": report.message_content[:500] if report.message_content else None,
            "scam_type": report.scam_type,
            "description": report.description[:1000],
            "reporter_location": report.reporter_location,
            "financial_loss": report.financial_loss,
            "currency": report.currency,
            "status": "verified_pending",
            "upvotes": 0,
        }

        doc_id = save_crowd_report(report_data)

        return {
            "success": True,
            "report_id": doc_id,
            "message": "Thank you for helping protect the community! Your report has been submitted.",
            "next_steps": [
                "Report will be reviewed and added to our shared database",
                "Other users will be warned about this scam",
                "Consider reporting to local authorities and FTC (reportfraud.ftc.gov)"
            ]
        }

    except Exception as e:
        logger.error(f"Report submission error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit report: {str(e)}")


@router.get("/list")
async def list_reports(limit: int = 50, report_type: Optional[str] = None):
    """Get crowd-sourced scam reports."""
    try:
        reports = get_crowd_reports(limit=limit)

        if report_type:
            reports = [r for r in reports if r.get('report_type') == report_type]

        return {
            "total": len(reports),
            "reports": reports
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check")
async def check_in_database(request: CheckRequest):
    """Check if phone/email/domain is in scam database."""
    try:
        result = check_crowd_database(
            phone=request.phone,
            domain=request.domain
        )

        return {
            "is_known_scam": result['is_known_scam'],
            "found": result['found'],
            "report_count": result['report_count'],
            "recent_reports": result['reports'][:3],
            "warning": f"This {'phone/email/domain' } has been reported {result['report_count']} time(s) as a scam!" if result['found'] else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def report_stats():
    """Get statistics about crowd-sourced reports."""
    try:
        reports = get_crowd_reports(limit=1000)

        type_counts = {}
        scam_type_counts = {}
        location_counts = {}
        total_loss = 0

        for r in reports:
            rt = r.get('report_type', 'unknown')
            type_counts[rt] = type_counts.get(rt, 0) + 1

            st = r.get('scam_type', 'Unknown')
            if st:
                scam_type_counts[st] = scam_type_counts.get(st, 0) + 1

            loc = r.get('reporter_location', 'Unknown')
            location_counts[loc] = location_counts.get(loc, 0) + 1

            if r.get('financial_loss'):
                total_loss += r['financial_loss']

        return {
            "total_reports": len(reports),
            "by_type": type_counts,
            "by_scam_type": dict(sorted(scam_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "by_location": dict(sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "total_reported_loss": round(total_loss, 2),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
