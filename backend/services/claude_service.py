"""
Claude AI service — all Anthropic API calls for the Lab Report Analyzer.
Uses tool_use for reliable structured output. Model: claude-sonnet-4-6.
Prompt caching applied to large reference-data system prompts.
"""
import json
import os
from pathlib import Path
from typing import Optional

import anthropic

from .cvd_calculator import (
    calculate_cvd_risk_sri_lanka,
    calculate_cha2ds2_vasc,
    mg_dl_to_mmol,
    tg_mg_dl_to_mmol,
)
from .pattern_engine import get_patterns_summary

_client: Optional[anthropic.Anthropic] = None

MODEL = "claude-sonnet-4-6"
REF_DIR = Path(__file__).parent.parent / "references"


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _load_ref(filename: str) -> dict:
    with open(REF_DIR / filename) as f:
        return json.load(f)


def _ref_summary() -> str:
    """Compact reference data for system prompt caching."""
    rr = _load_ref("reference_ranges.json")
    cv = _load_ref("critical_values.json")
    sg = _load_ref("severity_grading.json")
    mg = _load_ref("management_guidelines.json")
    ap = _load_ref("action-plan-guidelines.json")

    return f"""=== REFERENCE RANGES (key analytes) ===
{json.dumps({k: v for k, v in rr.items() if k in ['haematology','lipids','liver_function','thyroid','biochemistry']}, indent=2)[:3000]}

=== CRITICAL VALUES ===
{json.dumps(cv, indent=2)[:2000]}

=== SEVERITY GRADING ===
{json.dumps(sg, indent=2)[:2000]}

=== MANAGEMENT GUIDELINES (summary) ===
{json.dumps({k: v.get('first_line','') for k,v in mg.get('conditions',{}).items()}, indent=2)[:2000]}

=== CLINICAL PATTERNS ===
{get_patterns_summary()[:3000]}

=== ACTION PLAN FRAMEWORK ===
Diet pattern: {ap['diet']['recommended_pattern']}
Key LDL-lowering: {json.dumps(ap['diet']['ldl_lowering_foods'], indent=2)[:800]}
Exercise minimum: {ap['exercise']['minimum_aerobic']}
Alcohol position: {ap['alcohol']['position']}
"""


# ── Tool definitions ───────────────────────────────────────────

_PARSE_LABS_TOOL = {
    "name": "parse_lab_results",
    "description": "Parse raw lab report text or transcribed image into a structured array of analyte objects.",
    "input_schema": {
        "type": "object",
        "properties": {
            "lab_results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "panel": {"type": "string"},
                        "analyte": {"type": "string"},
                        "result": {"type": "string"},
                        "unit": {"type": "string"},
                        "lab_ref_range": {"type": "string"},
                        "standard_ref_range": {"type": "string"},
                        "status": {"type": "string", "enum": ["normal", "low", "high", "critical"]},
                        "severity": {"type": "string", "enum": ["normal", "mild", "moderate", "severe", "critical"]},
                        "is_critical": {"type": "boolean"},
                        "note": {"type": "string"}
                    },
                    "required": ["panel", "analyte", "result", "unit", "status", "severity", "is_critical"]
                }
            }
        },
        "required": ["lab_results"]
    }
}

_CLINICAL_ANALYSIS_TOOL = {
    "name": "clinical_analysis",
    "description": "Produce a comprehensive clinical interpretation, action plan, and follow-up plan for lab results.",
    "input_schema": {
        "type": "object",
        "properties": {
            "critical_values": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of critical value descriptions requiring immediate action"
            },
            "key_findings": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Top 3–5 most clinically significant findings as plain sentences"
            },
            "clinical_patterns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pattern_id": {"type": "string"},
                        "name": {"type": "string"},
                        "evidence": {"type": "string"},
                        "differentials": {"type": "array", "items": {"type": "string"}},
                        "significance": {"type": "string"}
                    }
                }
            },
            "further_investigations": {
                "type": "array",
                "items": {"type": "string"}
            },
            "management_suggestions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "condition": {"type": "string"},
                        "suggestion": {"type": "string"},
                        "source": {"type": "string"}
                    }
                }
            },
            "action_plan": {
                "type": "object",
                "properties": {
                    "diet": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string"},
                            "priority_reduces": {"type": "array", "items": {"type": "string"}},
                            "priority_increases": {"type": "array", "items": {"type": "string"}},
                            "practical_upgrade": {"type": "string"},
                            "supplements": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "exercise": {
                        "type": "object",
                        "properties": {
                            "aerobic_target": {"type": "string"},
                            "resistance": {"type": "string"},
                            "daily_habit": {"type": "string"},
                            "intensity_guide": {"type": "string"},
                            "sample_week": {"type": "string"},
                            "twelve_week_target": {"type": "string"}
                        }
                    },
                    "sleep": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string"},
                            "key_advice": {"type": "string"},
                            "osa_screen": {"type": "string"}
                        }
                    },
                    "alcohol": {
                        "type": "object",
                        "properties": {
                            "recommendation": {"type": "string"},
                            "reason": {"type": "string"}
                        }
                    }
                }
            },
            "follow_up_plan": {
                "type": "object",
                "properties": {
                    "repeat_tests": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "test": {"type": "string"},
                                "interval": {"type": "string"},
                                "reason": {"type": "string"}
                            }
                        }
                    },
                    "red_flags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "3–5 patient-specific symptoms that warrant immediate A&E attendance"
                    }
                }
            },
            "patient_summary": {
                "type": "string",
                "description": "Plain-language 3–4 sentence summary suitable for the patient"
            }
        },
        "required": ["critical_values", "key_findings", "clinical_patterns", "further_investigations",
                     "management_suggestions", "action_plan", "follow_up_plan", "patient_summary"]
    }
}


async def parse_lab_results(
    lab_text: str | None,
    image_b64: str | None,
    image_media_type: str | None,
) -> list[dict]:
    """Call 1: Parse raw lab text or image into structured analyte array."""
    client = _get_client()

    system_prompt = f"""You are a clinical laboratory expert.
Parse the provided lab results into a structured JSON array using the parse_lab_results tool.

IMPORTANT RULES:
1. Use the standard reference ranges provided below — not just the lab's own ranges.
2. Sri Lankan labs often report cholesterol in mg/dL. Note the unit and do NOT convert the value — keep as reported.
3. Classify status: normal / low / high / critical
4. Classify severity: normal / mild / moderate / severe / critical
5. is_critical = true only for CRITICAL VALUES that need immediate action.
6. Group results by panel (e.g. "Complete Blood Count", "Lipid Profile", "Liver Function Tests").

{_ref_summary()[:4000]}
"""

    if image_b64 and image_media_type:
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_media_type,
                        "data": image_b64,
                    }
                },
                {"type": "text", "text": "Parse all lab values from this image into structured JSON using the parse_lab_results tool."}
            ]
        }]
    else:
        messages = [{
            "role": "user",
            "content": f"Parse the following lab results:\n\n{lab_text}"
        }]

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        tools=[_PARSE_LABS_TOOL],
        tool_choice={"type": "tool", "name": "parse_lab_results"},
        messages=messages,
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "parse_lab_results":
            return block.input.get("lab_results", [])
    return []


async def run_clinical_analysis(
    parsed_labs: list[dict],
    patient: dict,
    cvd_factors: dict | None,
    cvd_risk_result: dict | None,
) -> dict:
    """Call 2: Full clinical analysis, action plan, and follow-up plan."""
    client = _get_client()

    ref_data = _ref_summary()
    ap_data = _load_ref("action-plan-guidelines.json")
    fu_data = ap_data.get("followup_timelines", {})
    red_flag_data = ap_data.get("red_flags", {})

    system_prompt = f"""You are Dr. D. R. Gamalathge's clinical AI assistant (SLMC No. 36999, Sri Lanka).
Provide evidence-based clinical analysis aligned with WHO · NICE · ESC/EAS guidelines.
NO Australian guidelines (no RACGP, no Heart Foundation Australia).
Patient population: Urban Sri Lankan, South Asian ethnicity.

{ref_data}

=== FOLLOW-UP TIMELINES (NICE NG238 2023 / ADA 2024 / ISH 2020) ===
{json.dumps(fu_data, indent=2)[:2000]}

=== RED FLAG SYMPTOMS (include 1990 — Suwa Seriya ambulance) ===
{json.dumps(red_flag_data, indent=2)[:1500]}

=== ACTION PLAN FRAMEWORK ===
Diet: {ap_data['diet']['recommended_pattern']}
LDL foods: {json.dumps(ap_data['diet']['ldl_lowering_foods'])[:500]}
Exercise min: {json.dumps(ap_data['exercise']['minimum_aerobic'])}
Alcohol: {ap_data['alcohol']['position']}
SL accessibility: {json.dumps(ap_data['exercise']['accessibility_sri_lanka'])[:300]}
"""

    user_content = f"""
Patient: {patient.get('name','Unknown')}, Age {patient.get('age','?')}, Sex {patient.get('sex','?')}
Indication: {patient.get('indication','Not specified')}
Medical history: {patient.get('history','None')}
Medications: {patient.get('medications','None')}

PARSED LAB RESULTS:
{json.dumps(parsed_labs, indent=2)}

CVD RISK FACTORS:
{json.dumps(cvd_factors or {}, indent=2)}

CVD RISK RESULT:
{json.dumps(cvd_risk_result or {}, indent=2)}

Please produce a complete clinical analysis using the clinical_analysis tool. Include:
1. Precise identification of all critical values
2. Top 3–5 key findings
3. Recognised clinical patterns (use the pattern library provided)
4. Further investigations — prioritised
5. Management suggestions citing WHO/NICE/ESC sources
6. Personalised Action Plan (Mediterranean diet for urban SL; FITT exercise; sleep; alcohol per WHO 2023)
7. Follow-Up Plan with condition-specific test intervals from NICE NG238/ADA 2024 + 3–5 red flag symptoms (include 1990 emergency number)
8. Patient-friendly summary (plain English, 3–4 sentences)
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=6000,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        tools=[_CLINICAL_ANALYSIS_TOOL],
        tool_choice={"type": "tool", "name": "clinical_analysis"},
        messages=[{"role": "user", "content": user_content}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "clinical_analysis":
            return block.input
    return {}


def run_cvd_risk(parsed_labs: list[dict], patient: dict, cvd_factors: dict | None) -> dict | None:
    """
    Extract lipid values from parsed labs, convert units, run WHO SEAR-B calculator.
    Returns CVD risk dict or None if insufficient data.
    """
    if not cvd_factors and not patient:
        return None

    age = patient.get("age")
    sex = patient.get("sex", "male").lower()
    if not age:
        return None

    cvd = cvd_factors or {}

    # Extract lipid values from parsed labs (handle mg/dL or mmol/L)
    tc_mmol = hdl_mmol = ldl_mmol = tg_mmol = None
    for lab in parsed_labs:
        name_lower = lab.get("analyte", "").lower()
        result_str = lab.get("result", "")
        unit = lab.get("unit", "").lower()
        try:
            val = float(result_str.replace(",", "").split()[0])
        except (ValueError, IndexError):
            continue

        is_mg = "mg" in unit

        if "total chol" in name_lower or (name_lower == "cholesterol" and "hdl" not in name_lower and "ldl" not in name_lower):
            tc_mmol = mg_dl_to_mmol(val) if is_mg else val
        elif "hdl" in name_lower:
            hdl_mmol = mg_dl_to_mmol(val) if is_mg else val
        elif "ldl" in name_lower:
            ldl_mmol = mg_dl_to_mmol(val) if is_mg else val
        elif "triglyc" in name_lower or "tg" == name_lower:
            tg_mmol = tg_mg_dl_to_mmol(val) if is_mg else val

    sbp = cvd.get("bp_systolic") or 130

    # Determine BMI
    bmi = None
    h = cvd.get("height_cm")
    w = cvd.get("weight_kg")
    if h and w:
        bmi = round(w / ((h / 100) ** 2), 1)

    result = calculate_cvd_risk_sri_lanka(
        age=age,
        sex=sex,
        sbp=sbp,
        tc_mmol=tc_mmol,
        smoker=(cvd.get("smoking_status") == "current"),
        diabetes=(cvd.get("diabetes_status") in ("type1", "type2")),
        on_bp_meds=bool(cvd.get("on_bp_meds")),
        on_statins=bool(cvd.get("on_statins")),
        egfr=cvd.get("egfr"),
        hdl_mmol=hdl_mmol,
        family_hx_cvd=bool(cvd.get("family_history_cvd")),
        known_cvd=bool(cvd.get("personal_history_cvd")),
        fh_suspected=bool(cvd.get("familial_hypercholesterolaemia")),
        severe_ckd=(cvd.get("egfr") is not None and cvd.get("egfr") < 30),
        bmi=bmi,
        waist_cm=cvd.get("waist_cm"),
    )

    # Add CHA2DS2-VASc if AF present
    if cvd.get("af"):
        cha = calculate_cha2ds2_vasc(
            hypertension=(sbp >= 140),
            age=age,
            diabetes=(cvd.get("diabetes_status") in ("type1", "type2")),
            sex_female=(sex == "female"),
        )
        result["cha2ds2_vasc"] = cha

    # Add cholesterol values used
    result["lipids_used"] = {
        "tc_mmol": tc_mmol,
        "hdl_mmol": hdl_mmol,
        "ldl_mmol": ldl_mmol,
        "tg_mmol": tg_mmol,
        "tc_hdl_ratio": round(tc_mmol / hdl_mmol, 2) if tc_mmol and hdl_mmol else None,
    }
    result["inputs"] = {
        "age": age, "sex": sex, "sbp": sbp,
        "smoker": cvd.get("smoking_status") == "current",
        "smoking_type": cvd.get("smoking_type"),
        "diabetes": cvd.get("diabetes_status"),
        "on_bp_meds": cvd.get("on_bp_meds"),
        "on_statins": cvd.get("on_statins"),
        "bmi": bmi,
        "waist_cm": cvd.get("waist_cm"),
    }

    return result
