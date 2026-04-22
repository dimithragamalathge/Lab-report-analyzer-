"use client";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ChevronDown } from "lucide-react";
import type { PatientFormValues } from "@/lib/types";

// ── Zod schema ─────────────────────────────────────────────────
const schema = z.object({
  name:        z.string().min(1, "Name is required"),
  age:         z.coerce.number().min(1).max(120).or(z.literal("")),
  sex:         z.enum(["male", "female", "other", ""]),
  dob:         z.string().optional(),
  indication:  z.string().optional(),
  history:     z.string().optional(),
  medications: z.string().optional(),
  allergies:   z.string().optional(),

  smoking_status:  z.enum(["current", "ex", "never", ""]).optional(),
  smoking_type:    z.enum(["cigarettes", "bidis", "hookah", "chewing", "mixed"]).optional(),
  pack_years:      z.coerce.number().min(0).optional().or(z.literal("")),
  years_since_quit:z.coerce.number().min(0).optional().or(z.literal("")),
  bp_systolic:     z.coerce.number().min(60).max(260).optional().or(z.literal("")),
  bp_diastolic:    z.coerce.number().min(30).max(160).optional().or(z.literal("")),
  on_bp_meds:      z.boolean().default(false),
  on_statins:      z.boolean().default(false),
  diabetes_status: z.enum(["none", "pre", "type1", "type2", ""]).optional(),
  diabetes_years:  z.coerce.number().min(0).optional().or(z.literal("")),
  on_insulin:      z.boolean().default(false),
  family_history_cvd:            z.boolean().default(false),
  personal_history_cvd:          z.boolean().default(false),
  af:                            z.boolean().default(false),
  egfr:                          z.coerce.number().min(0).max(200).optional().or(z.literal("")),
  familial_hypercholesterolaemia:z.boolean().default(false),
  severe_mental_illness:         z.boolean().default(false),
  height_cm:  z.coerce.number().min(50).max(250).optional().or(z.literal("")),
  weight_kg:  z.coerce.number().min(2).max(300).optional().or(z.literal("")),
  waist_cm:   z.coerce.number().min(30).max(200).optional().or(z.literal("")),
  report_date:z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  data: Partial<PatientFormValues>;
  onChange: (d: PatientFormValues) => void;
  onNext: () => void;
  onBack: () => void;
}

// ── Shared field components ─────────────────────────────────────
function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs uppercase tracking-widest text-ink-muted mb-1">{label}</label>
      {children}
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
    </div>
  );
}

const inputCls = "w-full rounded-lg border border-rule bg-white px-3 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-accent";
const selectCls = `${inputCls} appearance-none`;

function Check({ label, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label className="flex items-center gap-2 cursor-pointer">
      <input type="checkbox" className="accent-accent w-4 h-4" {...props} />
      <span className="text-sm text-ink">{label}</span>
    </label>
  );
}

// ── Accordion section ───────────────────────────────────────────
function AccordionSection({
  title, open, onToggle, children,
}: { title: string; open: boolean; onToggle: () => void; children: React.ReactNode }) {
  return (
    <div className="border border-rule rounded-xl overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 bg-white text-left"
      >
        <span className="text-sm font-semibold text-ink">{title}</span>
        <ChevronDown
          size={18}
          className={`text-ink-muted transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>
      {open && <div className="px-4 pb-4 pt-2 bg-white space-y-4">{children}</div>}
    </div>
  );
}

// ── Main form ───────────────────────────────────────────────────
export default function Step2PatientForm({ data, onChange, onNext, onBack }: Props) {
  const today = new Date().toISOString().slice(0, 10);
  const [open, setOpen] = useState<Record<string, boolean>>({
    identity: true, clinical: false, cvd: false, settings: false,
  });
  const toggle = (k: string) => setOpen((p) => ({ ...p, [k]: !p[k] }));

  const { register, handleSubmit, watch, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      ...data,
      on_bp_meds: data.on_bp_meds ?? false,
      on_statins: data.on_statins ?? false,
      on_insulin: data.on_insulin ?? false,
      family_history_cvd: data.family_history_cvd ?? false,
      personal_history_cvd: data.personal_history_cvd ?? false,
      af: data.af ?? false,
      familial_hypercholesterolaemia: data.familial_hypercholesterolaemia ?? false,
      severe_mental_illness: data.severe_mental_illness ?? false,
      report_date: data.report_date ?? today,
      sex: data.sex ?? "",
      smoking_status: data.smoking_status ?? "",
      diabetes_status: data.diabetes_status ?? "",
    },
  });

  const smokingStatus = watch("smoking_status");

  const onSubmit = (values: FormValues) => {
    onChange(values as PatientFormValues);
    onNext();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <h2 className="text-2xl font-serif text-ink">Patient Details</h2>
        <p className="text-sm text-ink-sub mt-1">Fill in as much as available.</p>
      </div>

      {/* A: Identity */}
      <AccordionSection title="A  Patient Identity" open={open.identity} onToggle={() => toggle("identity")}>
        <Field label="Full Name *" error={errors.name?.message}>
          <input {...register("name")} placeholder="e.g. Priya Fernando" className={inputCls} />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Age" error={errors.age?.message}>
            <input {...register("age")} type="number" placeholder="35" className={inputCls} />
          </Field>
          <Field label="Sex">
            <select {...register("sex")} className={selectCls}>
              <option value="">Select</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </Field>
        </div>
        <Field label="Date of Birth">
          <input {...register("dob")} type="date" className={inputCls} />
        </Field>
      </AccordionSection>

      {/* B: Clinical context */}
      <AccordionSection title="B  Clinical Context" open={open.clinical} onToggle={() => toggle("clinical")}>
        <Field label="Indication / Reason for Test">
          <input {...register("indication")} placeholder="e.g. Routine annual screen" className={inputCls} />
        </Field>
        <Field label="Medical History">
          <textarea {...register("history")} rows={3} placeholder="e.g. T2DM, Hypertension" className={`${inputCls} resize-none`} />
        </Field>
        <Field label="Current Medications">
          <textarea {...register("medications")} rows={3} placeholder="e.g. Metformin 500mg BD, Atorvastatin 20mg ON" className={`${inputCls} resize-none`} />
        </Field>
        <Field label="Allergies">
          <input {...register("allergies")} placeholder="e.g. Penicillin" className={inputCls} />
        </Field>
      </AccordionSection>

      {/* C: CVD risk factors */}
      <AccordionSection title="C  CVD Risk Factors" open={open.cvd} onToggle={() => toggle("cvd")}>
        <Field label="Smoking Status">
          <select {...register("smoking_status")} className={selectCls}>
            <option value="">Select</option>
            <option value="never">Never</option>
            <option value="ex">Ex-smoker</option>
            <option value="current">Current</option>
          </select>
        </Field>

        {smokingStatus === "current" && (
          <>
            <Field label="Smoking Type">
              <select {...register("smoking_type")} className={selectCls}>
                <option value="">Select</option>
                <option value="cigarettes">Cigarettes</option>
                <option value="bidis">Bidis</option>
                <option value="hookah">Hookah</option>
                <option value="chewing">Chewing tobacco</option>
                <option value="mixed">Mixed</option>
              </select>
            </Field>
            <Field label="Pack-years">
              <input {...register("pack_years")} type="number" placeholder="e.g. 10" className={inputCls} />
            </Field>
          </>
        )}
        {smokingStatus === "ex" && (
          <Field label="Years since quit">
            <input {...register("years_since_quit")} type="number" placeholder="e.g. 3" className={inputCls} />
          </Field>
        )}

        <div className="grid grid-cols-2 gap-3">
          <Field label="BP Systolic (mmHg)">
            <input {...register("bp_systolic")} type="number" placeholder="120" className={inputCls} />
          </Field>
          <Field label="BP Diastolic (mmHg)">
            <input {...register("bp_diastolic")} type="number" placeholder="80" className={inputCls} />
          </Field>
        </div>

        <div className="space-y-2">
          <Check label="On antihypertensive medication" {...register("on_bp_meds")} />
          <Check label="On statin therapy" {...register("on_statins")} />
        </div>

        <Field label="Diabetes Status">
          <select {...register("diabetes_status")} className={selectCls}>
            <option value="">Select</option>
            <option value="none">None</option>
            <option value="pre">Pre-diabetes</option>
            <option value="type1">Type 1</option>
            <option value="type2">Type 2</option>
          </select>
        </Field>

        <div className="grid grid-cols-2 gap-3">
          <Field label="Years with diabetes">
            <input {...register("diabetes_years")} type="number" placeholder="e.g. 5" className={inputCls} />
          </Field>
          <Field label="eGFR (mL/min/1.73m²)">
            <input {...register("egfr")} type="number" placeholder="e.g. 65" className={inputCls} />
          </Field>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Field label="Height (cm)">
            <input {...register("height_cm")} type="number" placeholder="165" className={inputCls} />
          </Field>
          <Field label="Weight (kg)">
            <input {...register("weight_kg")} type="number" placeholder="70" className={inputCls} />
          </Field>
        </div>

        <Field label="Waist circumference (cm)" error={undefined}>
          <input {...register("waist_cm")} type="number" placeholder="M >90 / F >80 = central obesity (South Asian)" className={inputCls} />
        </Field>

        <div className="space-y-2 pt-1">
          <Check label="On insulin" {...register("on_insulin")} />
          <Check label="Family history of premature CVD" {...register("family_history_cvd")} />
          <Check label="Personal history of CVD" {...register("personal_history_cvd")} />
          <Check label="Atrial fibrillation (AF)" {...register("af")} />
          <Check label="Familial hypercholesterolaemia (suspected/confirmed)" {...register("familial_hypercholesterolaemia")} />
          <Check label="Severe mental illness" {...register("severe_mental_illness")} />
        </div>
      </AccordionSection>

      {/* D: Settings */}
      <AccordionSection title="D  Report Settings" open={open.settings} onToggle={() => toggle("settings")}>
        <Field label="Report Date">
          <input {...register("report_date")} type="date" className={inputCls} />
        </Field>
      </AccordionSection>

      <button
        type="submit"
        className="w-full py-3.5 bg-accent text-white font-medium rounded-xl"
      >
        Run Analysis
      </button>
    </form>
  );
}
