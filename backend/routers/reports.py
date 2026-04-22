from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select, func, delete
from pathlib import Path

from models.database import AsyncSessionLocal
from models.orm import Report
from models.schemas import ReportSummary, ReportListResponse

router = APIRouter(prefix="/api")


@router.get("/reports", response_model=ReportListResponse)
async def list_reports(page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    async with AsyncSessionLocal() as db:
        count_result = await db.execute(select(func.count()).select_from(Report))
        total = count_result.scalar() or 0

        result = await db.execute(
            select(Report)
            .order_by(Report.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        reports = result.scalars().all()

    return ReportListResponse(
        reports=[
            ReportSummary(
                id=r.id,
                created_at=r.created_at,
                patient_name=r.patient_name,
                patient_age=r.patient_age,
                patient_sex=r.patient_sex,
                status=r.status,
                pdf_path=r.pdf_path,
            )
            for r in reports
        ],
        total=total,
    )


@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Report).where(Report.id == report_id))
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

    import json
    return {
        "id": report.id,
        "created_at": str(report.created_at),
        "patient_name": report.patient_name,
        "patient_age": report.patient_age,
        "patient_sex": report.patient_sex,
        "patient_dob": report.patient_dob,
        "indication": report.indication,
        "medical_history": report.medical_history,
        "medications": report.medications,
        "status": report.status,
        "parsed_labs": json.loads(report.parsed_labs or "[]"),
        "critical_values": json.loads(report.critical_values or "[]"),
        "clinical_patterns": json.loads(report.clinical_patterns or "[]"),
        "cvd_risk_result": json.loads(report.cvd_risk_result or "{}"),
        "further_investigations": json.loads(report.further_investigations or "[]"),
        "management_suggestions": json.loads(report.management_suggestions or "[]"),
        "action_plan": json.loads(report.action_plan or "{}"),
        "follow_up_plan": json.loads(report.follow_up_plan or "{}"),
        "patient_summary": report.patient_summary,
        "doctor_edits": report.doctor_edits,
        "pdf_url": f"/api/reports/{report.id}/pdf" if report.pdf_path else None,
    }


@router.get("/reports/{report_id}/pdf")
async def get_report_pdf(report_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Report).where(Report.id == report_id))
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        if not report.pdf_path:
            raise HTTPException(status_code=404, detail="PDF not yet generated")

    pdf_path = Path(report.pdf_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"report_{report_id[:8]}.pdf",
    )


@router.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Report).where(Report.id == report_id))
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if report.pdf_path:
            pdf = Path(report.pdf_path)
            if pdf.exists():
                pdf.unlink()

        await db.execute(delete(Report).where(Report.id == report_id))
        await db.commit()

    return {"success": True}
