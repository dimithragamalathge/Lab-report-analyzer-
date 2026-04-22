"use client";
import { useState } from "react";
import WizardShell from "@/components/wizard/WizardShell";
import Step1LabInput, { type LabInputData } from "@/components/wizard/Step1LabInput";
import Step2PatientForm from "@/components/wizard/Step2PatientForm";
import Step3Analyzing from "@/components/wizard/Step3Analyzing";
import Step4DraftReview from "@/components/wizard/Step4DraftReview";
import Step5Complete from "@/components/wizard/Step5Complete";
import { analyzeStart, analyzeConfirm } from "@/lib/api";
import type { DraftResponse, PatientFormValues } from "@/lib/types";

export default function AnalyzePage() {
  const [step, setStep] = useState(1);
  const [error, setError] = useState("");

  // Step 1 state
  const [labInput, setLabInput] = useState<LabInputData>({
    labText: "", uploadIds: [], uploadedFiles: [],
  });

  // Step 2 state
  const [patient, setPatient] = useState<Partial<PatientFormValues>>({});

  // Step 3/4 state
  const [reportId, setReportId] = useState("");
  const [draft, setDraft] = useState<DraftResponse | null>(null);
  const [confirming, setConfirming] = useState(false);

  // Step 1 → Step 2
  const goStep2 = () => { setError(""); setStep(2); };

  // Step 2 → Step 3 (fire API call)
  const goStep3 = async (patientValues: PatientFormValues) => {
    setPatient(patientValues);
    setStep(3);
    setError("");

    const cvdFields = [
      "smoking_status", "smoking_type", "pack_years", "years_since_quit",
      "bp_systolic", "bp_diastolic", "on_bp_meds", "on_statins",
      "diabetes_status", "diabetes_years", "on_insulin",
      "family_history_cvd", "personal_history_cvd", "af", "egfr",
      "familial_hypercholesterolaemia", "severe_mental_illness",
      "height_cm", "weight_kg", "waist_cm",
    ] as const;

    const patientPayload: Record<string, unknown> = {
      name: patientValues.name,
      age: patientValues.age || undefined,
      sex: patientValues.sex || undefined,
      dob: patientValues.dob || undefined,
      indication: patientValues.indication || undefined,
      history: patientValues.history || undefined,
      medications: patientValues.medications || undefined,
      allergies: patientValues.allergies || undefined,
    };

    const cvdPayload: Record<string, unknown> = {};
    for (const k of cvdFields) {
      const v = patientValues[k];
      if (v !== "" && v !== undefined && v !== null) cvdPayload[k] = v;
    }

    try {
      const res = await analyzeStart({
        lab_text: labInput.labText || undefined,
        upload_ids: labInput.uploadIds.length ? labInput.uploadIds : undefined,
        patient: patientPayload,
        cvd_factors: Object.keys(cvdPayload).length ? cvdPayload : undefined,
        report_settings: { report_date: patientValues.report_date || undefined },
      });
      setReportId(res.report_id);
      setDraft(res.draft);
      setStep(4);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Analysis failed");
      setStep(2);
    }
  };

  // Step 4 → Step 5 (confirm + generate PDF)
  const goStep5 = async (doctorNotes: string) => {
    setConfirming(true);
    setError("");
    try {
      await analyzeConfirm(reportId, doctorNotes || undefined);
      setStep(5);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "PDF generation failed");
    } finally {
      setConfirming(false);
    }
  };

  const handleBack = () => {
    if (step === 2) setStep(1);
    if (step === 4) setStep(2);
  };

  return (
    <WizardShell step={step} onBack={handleBack}>
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
          {error}
        </div>
      )}

      {step === 1 && (
        <Step1LabInput data={labInput} onChange={setLabInput} onNext={goStep2} />
      )}
      {step === 2 && (
        <Step2PatientForm data={patient} onChange={setPatient} onNext={goStep3} onBack={() => setStep(1)} />
      )}
      {step === 3 && <Step3Analyzing />}
      {step === 4 && draft && (
        <Step4DraftReview
          reportId={reportId}
          draft={draft}
          onConfirm={goStep5}
          confirming={confirming}
        />
      )}
      {step === 5 && <Step5Complete reportId={reportId} />}
    </WizardShell>
  );
}
