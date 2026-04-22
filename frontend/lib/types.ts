export interface LabRow {
  panel: string;
  analyte: string;
  result: string;
  unit: string;
  lab_ref_range?: string;
  reference?: string;
  status: string;
  severity: "normal" | "mild" | "moderate" | "severe" | "critical" | "low" | "high";
  note?: string;
}

export interface CriticalValue {
  analyte: string;
  result: string;
  unit: string;
  note?: string;
}

export interface Finding {
  finding: string;
}

export interface ClinicalPattern {
  name: string;
  evidence: string;
}

export interface CVDRisk {
  risk_percent_10yr: number | string;
  risk_category: "LOW" | "MODERATE" | "HIGH" | "VERY HIGH";
  method: string;
  reclassification_factors: string[];
  treatment_threshold_met: boolean;
  missing_variables: string[];
  clinical_override?: string;
}

export interface ActionPlan {
  diet: string;
  exercise: string;
  sleep: string;
  alcohol: string;
}

export interface FollowUpPlan {
  repeat_tests: string[];
  red_flags: string[];
}

export interface DraftResponse {
  critical_values: CriticalValue[];
  key_findings: Finding[];
  cvd_risk: CVDRisk;
  clinical_patterns: ClinicalPattern[];
  further_investigations: string[];
  management_suggestions: string[];
  action_plan: ActionPlan;
  follow_up_plan: FollowUpPlan;
  patient_summary: string;
}

export interface ReportSummary {
  id: string;
  created_at: string;
  patient_name: string;
  patient_age?: number;
  patient_sex?: string;
  status: string;
  pdf_path?: string;
}

export interface ReportDetail extends ReportSummary {
  patient_dob?: string;
  indication?: string;
  medical_history?: string;
  medications?: string;
  parsed_labs: LabRow[];
  critical_values: CriticalValue[];
  clinical_patterns: ClinicalPattern[];
  cvd_risk_result: CVDRisk;
  further_investigations: string[];
  management_suggestions: string[];
  action_plan: ActionPlan;
  follow_up_plan: FollowUpPlan;
  patient_summary: string;
  doctor_edits?: string;
  pdf_url?: string;
}

export interface PatientFormValues {
  name: string;
  age: number | "";
  sex: "male" | "female" | "other" | "";
  dob: string;
  indication: string;
  history: string;
  medications: string;
  allergies: string;
  smoking_status: "current" | "ex" | "never" | "";
  smoking_type?: "cigarettes" | "bidis" | "hookah" | "chewing" | "mixed";
  pack_years?: number | "";
  years_since_quit?: number | "";
  bp_systolic?: number | "";
  bp_diastolic?: number | "";
  on_bp_meds: boolean;
  on_statins: boolean;
  diabetes_status: "none" | "pre" | "type1" | "type2" | "";
  diabetes_years?: number | "";
  on_insulin: boolean;
  family_history_cvd: boolean;
  personal_history_cvd: boolean;
  af: boolean;
  egfr?: number | "";
  familial_hypercholesterolaemia: boolean;
  severe_mental_illness: boolean;
  height_cm?: number | "";
  weight_kg?: number | "";
  waist_cm?: number | "";
  report_date: string;
}
