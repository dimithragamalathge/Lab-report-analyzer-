from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    patient_name: Mapped[str] = mapped_column(String, nullable=False)
    patient_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    patient_sex: Mapped[str | None] = mapped_column(String, nullable=True)
    patient_dob: Mapped[str | None] = mapped_column(String, nullable=True)

    indication: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    medications: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)

    cvd_factors: Mapped[str | None] = mapped_column(Text, nullable=True)

    lab_input_type: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_lab_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    parsed_labs: Mapped[str | None] = mapped_column(Text, nullable=True)
    critical_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    clinical_patterns: Mapped[str | None] = mapped_column(Text, nullable=True)
    cvd_risk_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    further_investigations: Mapped[str | None] = mapped_column(Text, nullable=True)
    management_suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    draft_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    doctor_edits: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="analyzing")


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    report_id: Mapped[str | None] = mapped_column(String, nullable=True)
    original_name: Mapped[str | None] = mapped_column(String, nullable=True)
    file_type: Mapped[str | None] = mapped_column(String, nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
