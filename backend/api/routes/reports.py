"""GET /api/reports — report list and PDF export."""
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import Report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
async def list_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.generated_at.desc()).all()
    return [
        {
            "id": r.id,
            "event_id": r.event_id,
            "report_type": r.report_type,
            "pdf_url": r.pdf_url,
            "generated_at": str(r.generated_at),
        }
        for r in reports
    ]


@router.get("/{report_id}/export")
async def export_report_pdf(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    pdf_path = report.pdf_url
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path),
    )
