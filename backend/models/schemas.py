from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class PatientIn(BaseModel):
    name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    dob: Optional[str] = None
    indication: Optional[str] = None
    history: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None


class CVDFactorsIn(BaseModel):
    smoking_status: Optional[str] = None         # current | ex | never
    smoking_type: Optional[str] = None           # cigarettes | bidis | hookah | chewing | mixed
    pack_years: Optional[float] = None
    years_since_quit: Optional[float] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    on_bp_meds: Optional[bool] = None
    on_statins: Optional[bool] = None
    diabetes_status: Optional[str] = None        # none | pre | type1 | type2
    diabetes_years: Optional[int] = None
    on_insulin: Optional[bool] = None
    family_history_cvd: Optional[bool] = None
    personal_history_cvd: Optional[bool] = None
    af: Optional[bool] = None
    egfr: Optional[float] = None
    familial_hypercholesterolaemia: Optional[bool] = None
    severe_mental_illness: Optional[bool] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    waist_cm: Optional[float] = None


class ReportSettingsIn(BaseModel):
    report_date: Optional[str] = None
    lab_reference_ranges: Optional[str] = None


class AnalyzeStartRequest(BaseModel):
    lab_text: Optional[str] = None
    upload_ids: Optional[list[str]] = []
    patient: PatientIn
    cvd_factors: Optional[CVDFactorsIn] = None
    report_settings: Optional[ReportSettingsIn] = None


class AnalyzeConfirmRequest(BaseModel):
    report_id: str
    doctor_edits: Optional[str] = None


class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    file_type: str
    extracted_text: str


class DraftResponse(BaseModel):
    critical_values: list[Any] = []
    key_findings: list[str] = []
    cvd_risk: Optional[dict] = None
    clinical_patterns: list[Any] = []
    further_investigations: list[str] = []
    management_suggestions: list[Any] = []
    action_plan: Optional[dict] = None
    follow_up_plan: Optional[dict] = None
    patient_summary: str = ""


class AnalyzeStartResponse(BaseModel):
    report_id: str
    draft: DraftResponse


class AnalyzeConfirmResponse(BaseModel):
    report_id: str
    pdf_url: str
    status: str


class ReportSummary(BaseModel):
    id: str
    created_at: datetime
    patient_name: str
    patient_age: Optional[int]
    patient_sex: Optional[str]
    status: str
    pdf_path: Optional[str]


class ReportListResponse(BaseModel):
    reports: list[ReportSummary]
    total: int
