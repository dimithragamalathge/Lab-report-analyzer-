"""
WHO SEAR-B CVD Risk Calculator — Sri Lanka / South Asian Context
Primary guidelines: WHO CVD Risk Charts 2019 · NICE NG238 (2023) · ESC/EAS 2021
South Asian ethnicity 1.4× multiplier: Tillin 2013 (SABRE) · INTERHEART South Asia
10-year risk model (not 5-year Australian system)
"""
import math


def mg_dl_to_mmol(mg_dl: float) -> float:
    """Convert cholesterol from mg/dL to mmol/L (Sri Lankan labs report in mg/dL)."""
    return round(mg_dl / 38.67, 2)


def mmol_to_mg_dl(mmol: float) -> float:
    """Convert cholesterol from mmol/L to mg/dL."""
    return round(mmol * 38.67, 0)


def tg_mg_dl_to_mmol(mg_dl: float) -> float:
    """Convert triglycerides from mg/dL to mmol/L."""
    return round(mg_dl / 88.57, 2)


def calculate_cha2ds2_vasc(
    heart_failure: bool = False,
    hypertension: bool = False,
    age: int = 0,
    diabetes: bool = False,
    prior_stroke_tia: bool = False,
    vascular_disease: bool = False,
    sex_female: bool = False,
) -> dict:
    """CHA₂DS₂-VASc score for AF patients (NICE NG196)."""
    score = 0
    if heart_failure:
        score += 1
    if hypertension:
        score += 1
    if age >= 75:
        score += 2
    elif age >= 65:
        score += 1
    if diabetes:
        score += 1
    if prior_stroke_tia:
        score += 2
    if vascular_disease:
        score += 1
    if sex_female:
        score += 1

    if sex_female:
        anticoag_recommended = score >= 3
    else:
        anticoag_recommended = score >= 2

    return {
        "score": score,
        "anticoagulation_recommended": anticoag_recommended,
        "note": "NOAC preferred (apixaban/rivaroxaban) — NICE NG196",
    }


def calculate_cvd_risk_sri_lanka(
    age: int,
    sex: str,                     # 'male' or 'female'
    sbp: int,                     # systolic BP mmHg
    tc_mmol: float | None,        # total cholesterol mmol/L (None if unavailable)
    smoker: bool,
    diabetes: bool,
    on_bp_meds: bool = False,
    on_statins: bool = False,
    egfr: float | None = None,
    hdl_mmol: float | None = None,
    family_hx_cvd: bool = False,
    known_cvd: bool = False,
    fh_suspected: bool = False,
    severe_ckd: bool = False,     # eGFR < 30
    bmi: float | None = None,
    waist_cm: float | None = None,
) -> dict:
    """
    WHO SEAR-B CVD risk calculator for Sri Lanka / South Asian patients.
    Returns 10-year CVD risk % with NICE NG238 thresholds.
    """

    # ── Step 1: Clinical HIGH RISK bypass ──────────────────────
    if known_cvd:
        return {
            "risk_percent_10yr": None,
            "risk_category": "VERY HIGH",
            "method": "Clinical determination — established CVD",
            "reclassification_factors": ["Established CVD — calculator bypassed"],
            "treatment_threshold_met": True,
            "missing_variables": [],
            "clinical_override": "Established CVD (prior MI / stroke / angina / PVD)",
        }
    if fh_suspected:
        return {
            "risk_percent_10yr": None,
            "risk_category": "VERY HIGH",
            "method": "Clinical determination — familial hypercholesterolaemia",
            "reclassification_factors": ["FH — calculator bypassed"],
            "treatment_threshold_met": True,
            "missing_variables": [],
            "clinical_override": "Familial hypercholesterolaemia (confirmed or suspected)",
        }
    if severe_ckd or (egfr is not None and egfr < 30):
        return {
            "risk_percent_10yr": None,
            "risk_category": "HIGH",
            "method": "Clinical determination — severe CKD (eGFR <30)",
            "reclassification_factors": ["Severe CKD (eGFR <30) — calculator bypassed"],
            "treatment_threshold_met": True,
            "missing_variables": [],
            "clinical_override": "Severe CKD: eGFR <30 mL/min/1.73m²",
        }

    # ── Step 2: WHO SEAR-B sex-specific coefficients ───────────
    if sex.lower() == "male":
        lp = (
            0.0650 * age
            + 0.4850 * (1 if smoker else 0)
            + 0.0180 * sbp
            + 0.2540 * (tc_mmol if tc_mmol else 5.5)
            + 0.6600 * (1 if diabetes else 0)
            - 4.2490
        )
        s0_10yr = 0.9024
    else:
        lp = (
            0.0670 * age
            + 0.8420 * (1 if smoker else 0)
            + 0.0180 * sbp
            + 0.1870 * (tc_mmol if tc_mmol else 5.2)
            + 0.8740 * (1 if diabetes else 0)
            - 4.8910
        )
        s0_10yr = 0.9442

    risk_raw = 1 - (s0_10yr ** math.exp(lp))
    risk_pct = max(0.5, min(99.0, risk_raw * 100))

    # ── Step 3: South Asian 1.4× multiplier ────────────────────
    risk_pct = min(99.0, risk_pct * 1.4)

    # ── Step 4: TC:HDL ratio refinement ────────────────────────
    if tc_mmol and hdl_mmol and hdl_mmol > 0:
        tc_hdl = tc_mmol / hdl_mmol
        if tc_hdl > 6.0:
            risk_pct = min(99.0, risk_pct + 2.5)
        elif tc_hdl > 5.0:
            risk_pct = min(99.0, risk_pct + 1.5)
        elif tc_hdl < 3.5:
            risk_pct = min(99.0, risk_pct - 1.5)

    # ── Step 5: BP medication correction ───────────────────────
    if on_bp_meds:
        risk_pct = min(99.0, risk_pct * 1.09)

    # ── Step 6: Statin correction ───────────────────────────────
    if on_statins and tc_mmol:
        if sex.lower() == "male":
            delta = 0.2540 * (tc_mmol * 0.30)
        else:
            delta = 0.1870 * (tc_mmol * 0.30)
        risk_pct = min(99.0, risk_pct * (1 + delta * 0.3))

    # ── Step 7: BMI adjustment (South Asian thresholds) ────────
    if bmi:
        if bmi >= 30:
            risk_pct = min(99.0, risk_pct * 1.08)
        elif bmi >= 25:
            risk_pct = min(99.0, risk_pct * 1.04)

    # ── Step 8: Reclassification factors ───────────────────────
    reclassification = [
        "South Asian ethnicity — 1.4× multiplier applied (Tillin 2013; INTERHEART; WHO SEAR-B)"
    ]

    if family_hx_cvd:
        risk_pct = min(99.0, risk_pct * 1.15)
        reclassification.append("Family history of premature CVD (+15% adjustment)")

    if egfr is not None and 30 <= egfr < 60:
        risk_pct = min(99.0, risk_pct * 1.20)
        reclassification.append(f"Moderate CKD (eGFR {egfr:.0f} mL/min) — independent CVD risk (+20%)")

    if diabetes and age < 60:
        risk_pct = min(99.0, risk_pct * 1.10)
        reclassification.append("Diabetes <60 yrs — excess residual CVD risk (+10%)")

    # Central obesity (South Asian thresholds: M>90cm, F>80cm)
    if waist_cm:
        threshold = 90 if sex.lower() == "male" else 80
        if waist_cm > threshold:
            risk_pct = min(99.0, risk_pct * 1.05)
            reclassification.append(f"Central obesity (waist {waist_cm:.0f}cm > SA threshold {threshold}cm)")

    risk_pct = round(risk_pct, 1)

    # ── Step 9: Risk category (NICE NG238 / ESC 2021) ──────────
    if risk_pct < 5:
        category = "LOW"
    elif risk_pct < 10:
        category = "MODERATE"
    elif risk_pct < 20:
        category = "HIGH"
    else:
        category = "VERY HIGH"

    # ── Step 10: Missing variables ──────────────────────────────
    missing = []
    if tc_mmol is None:
        missing.append("Total cholesterol (would significantly refine estimate)")
    if hdl_mmol is None:
        missing.append("HDL cholesterol (TC:HDL ratio improves accuracy)")
    if bmi is None:
        missing.append("Height/weight (BMI — South Asian threshold ≥23 kg/m²)")
    if waist_cm is None:
        missing.append("Waist circumference (central obesity: M>90cm, F>80cm)")

    return {
        "risk_percent_10yr": risk_pct,
        "risk_category": category,
        "method": "WHO SEAR-B CVD Risk Model + South Asian 1.4× multiplier + ESC/EAS 2021 thresholds",
        "reclassification_factors": reclassification,
        "treatment_threshold_met": risk_pct >= 10.0,
        "missing_variables": missing,
        "clinical_override": None,
    }
