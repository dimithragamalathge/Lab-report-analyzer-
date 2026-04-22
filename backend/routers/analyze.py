import json
import uuid
from datetime import datetime, date

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from models.database import AsyncSessionLocal
from models.orm import Report, Upload
from models.schemas import (
    AnalyzeStartRequest, AnalyzeStartResponse, DraftResponse,
    AnalyzeConfirmRequest, AnalyzeConfirmResponse,
)
from services.claude_service import parse_lab_results, run_clinical_analysis, run_cvd_risk
from services.pdf_generator import build_medical_report

router = APIRouter(prefix="/api")


@router.post("/analyze/start", response_model=AnalyzeStartResponse)
async def analyze_start(req: AnalyzeStartRequest):
    report_id = str(uuid.uuid4())
    patient = req.patient.model_dump()
    cvd_factors = req.cvd_factors.model_dump() if req.cvd_factors else {}
    report_date = (req.report_settings.report_date if req.report_settings else None) or str(date.today())

    # Gather lab text
    lab_texts = []
    upload_records = []

    async with AsyncSessionLocal() as db:
        for uid in (req.upload_ids or []):
            result = await db.execute(select(Upload).where(Upload.id == uid))
            upload = result.scalar_one_or_none()
            if upload:
                upload_records.append(upload)
                if upload.extracted_text:
                    lab_texts.append(upload.extracted_text)

    if req.lab_text:
        lab_texts.insert(0, req.lab_text)

    combined_lab_text = "\n\n".join(lab_texts) if lab_texts else ""

    if not combined_lab_text:
        raise HTTPException(status_code=400, detail="No lab data provided — please upload a file or paste lab text.")

    # Call 1: Parse labs
    parsed_labs = await parse_lab_results(combined_lab_text, None, None)

    # CVD risk calculation
    cvd_risk_result = run_cvd_risk(parsed_labs, patient, cvd_factors)

    # Call 2: Clinical analysis
    analysis = await run_clinical_analysis(parsed_labs, patient, cvd_factors, cvd_risk_result)

    draft = DraftResponse(
        critical_values=analysis.get("critical_values", []),
        key_findings=analysis.get("key_findings", []),
        cvd_risk=cvd_risk_result,
        clinical_patterns=analysis.get("clinical_patterns", []),
        further_investigations=analysis.get("further_investigations", []),
        management_suggestions=analysis.get("management_suggestions", []),
        action_plan=analysis.get("action_plan"),
        follow_up_plan=analysis.get("follow_up_plan"),
        patient_summary=analysis.get("patient_summary", ""),
    )

    async with AsyncSessionLocal() as db:
        report = Report(
            id=report_id,
            patient_name=patient.get("name", "Unknown"),
            patient_age=patient.get("age"),
            patient_sex=patient.get("sex"),
            patient_dob=patient.get("dob"),
            indication=patient.get("indication"),
            medical_history=patient.get("history"),
            medications=patient.get("medications"),
            allergies=patient.get("allergies"),
            cvd_factors=json.dumps(cvd_factors),
            lab_input_type="text" if not upload_records else ("mixed" if req.lab_text else upload_records[0].file_type),
            raw_lab_text=combined_lab_text,
            parsed_labs=json.dumps(parsed_labs),
            critical_values=json.dumps(analysis.get("critical_values", [])),
            clinical_patterns=json.dumps(analysis.get("clinical_patterns", [])),
            cvd_risk_result=json.dumps(cvd_risk_result),
            further_investigations=json.dumps(analysis.get("further_investigations", [])),
            management_suggestions=json.dumps(analysis.get("management_suggestions", [])),
            action_plan=json.dumps(analysis.get("action_plan", {})),
            follow_up_plan=json.dumps(analysis.get("follow_up_plan", {})),
            draft_summary=json.dumps(draft.model_dump()),
            patient_summary=analysis.get("patient_summary", ""),
            status="draft",
        )
        db.add(report)

        # Link uploads to report
        for upload in upload_records:
            upload.report_id = report_id

        await db.commit()

    return AnalyzeStartResponse(report_id=report_id, draft=draft)


@router.post("/analyze/confirm", response_model=AnalyzeConfirmResponse)
async def analyze_confirm(req: AnalyzeConfirmRequest):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Report).where(Report.id == req.report_id))
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if req.doctor_edits:
            report.doctor_edits = req.doctor_edits

        parsed_labs = json.loads(report.parsed_labs or "[]")
        cvd_risk = json.loads(report.cvd_risk_result or "{}")
        management = json.loads(report.management_suggestions or "[]")
        patterns = json.loads(report.clinical_patterns or "[]")
        further = json.loads(report.further_investigations or "[]")
        critical = json.loads(report.critical_values or "[]")
        action_plan = json.loads(report.action_plan or "{}")
        follow_up_plan = json.loads(report.follow_up_plan or "{}")

        report_date_str = str(date.today())

        # Group labs by panel
        panels: dict[str, list] = {}
        for lab in parsed_labs:
            panel = lab.get("panel", "Other")
            panels.setdefault(panel, []).append(lab)

        results_by_panel = [
            {"panel": panel, "rows": rows}
            for panel, rows in panels.items()
        ]

        patient_info = {
            "name": report.patient_name,
            "id": report.id[:8].upper(),
            "age": str(report.patient_age or "—"),
            "sex": report.patient_sex or "—",
            "dob": report.patient_dob or "—",
            "indication": report.indication or "—",
            "history": report.medical_history or "—",
            "visit_date": report_date_str,
            "report_date": report_date_str,
        }

        pdf_path = f"generated_reports/{report.id}.pdf"

        build_medical_report(
            output_path=pdf_path,
            patient_info=patient_info,
            results_by_panel=results_by_panel,
            clinical_interpretation={
                "key_findings": json.loads(report.draft_summary or "{}").get("key_findings", []),
                "findings": [{"heading": p.get("name",""), "detail": p.get("evidence","")} for p in patterns],
                "severity_summary": [
                    {
                        "analyte": lab.get("analyte",""),
                        "result": f"{lab.get('result','')} {lab.get('unit','')}",
                        "severity": lab.get("severity","normal"),
                        "significance": lab.get("note","")
                    }
                    for lab in parsed_labs
                    if lab.get("severity","normal") != "normal"
                ]
            },
            critical_values=critical,
            further_investigations=further,
            management_suggestions=management,
            patient_summary=report.patient_summary or "",
            cvd_risk=cvd_risk,
            action_plan=action_plan,
            follow_up_plan=follow_up_plan,
            doctor_notes=report.doctor_edits,
        )

        report.pdf_path = pdf_path
        report.status = "completed"
        report.updated_at = datetime.utcnow()
        await db.commit()

    return AnalyzeConfirmResponse(
        report_id=req.report_id,
        pdf_url=f"/api/reports/{req.report_id}/pdf",
        status="completed",
    )
