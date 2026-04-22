"use client";
import { useState } from "react";
import type { DraftResponse } from "@/lib/types";

interface Props {
  reportId: string;
  draft: DraftResponse;
  onConfirm: (doctorNotes: string) => void;
  confirming: boolean;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-rule overflow-hidden">
      <div className="px-4 py-2.5 border-b border-rule bg-paper-alt">
        <p className="text-xs font-semibold uppercase tracking-widest text-ink-sub">{title}</p>
      </div>
      <div className="px-4 py-3">{children}</div>
    </div>
  );
}

export default function Step4DraftReview({ draft, onConfirm, confirming }: Props) {
  const [doctorNotes, setDoctorNotes] = useState("");

  const riskColour = {
    LOW: "text-green-700", MODERATE: "text-amber-700",
    HIGH: "text-accent", "VERY HIGH": "text-[#5a2418]",
  }[draft.cvd_risk?.risk_category ?? "LOW"] ?? "text-ink";

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-serif text-ink">Draft Review</h2>
        <p className="text-sm text-ink-sub mt-1">Review the findings, add notes, then generate the PDF.</p>
      </div>

      {/* Critical values */}
      {draft.critical_values?.length > 0 && (
        <div className="bg-[#5a2418] text-white rounded-xl p-4">
          <p className="text-xs font-bold tracking-widest uppercase mb-2">
            Critical Values — Immediate Review
          </p>
          {draft.critical_values.map((cv, i) => (
            <p key={i} className="text-sm font-mono">
              {cv.analyte}: {cv.result} {cv.unit}{cv.note ? ` — ${cv.note}` : ""}
            </p>
          ))}
        </div>
      )}

      {/* Key findings */}
      {draft.key_findings?.length > 0 && (
        <Section title="§ 01  Key Findings">
          <ol className="space-y-2 list-decimal list-inside">
            {draft.key_findings.map((f, i) => (
              <li key={i} className="text-sm text-ink italic">
                {typeof f === "string" ? f : f.finding}
              </li>
            ))}
          </ol>
        </Section>
      )}

      {/* CVD risk */}
      {draft.cvd_risk?.risk_category && (
        <Section title="§ 04  CVD Risk — WHO SEAR-B (10-year)">
          <div className="flex items-center gap-4">
            <div>
              <p className={`text-4xl font-bold ${riskColour}`}>
                {draft.cvd_risk.risk_percent_10yr}%
              </p>
              <p className="text-sm text-ink-sub">{draft.cvd_risk.risk_category}</p>
            </div>
            <div className="text-sm text-ink-sub space-y-1">
              <p>NICE NG238 statin threshold:{" "}
                <span className="font-medium">
                  {draft.cvd_risk.treatment_threshold_met ? "Met (≥10%) ✓" : "Not met (<10%)"}
                </span>
              </p>
              <p className="text-xs text-ink-muted">South Asian 1.4× calibration applied</p>
              {draft.cvd_risk.clinical_override && (
                <p className="text-xs text-accent font-medium">{draft.cvd_risk.clinical_override}</p>
              )}
            </div>
          </div>
          {draft.cvd_risk.reclassification_factors?.length > 0 && (
            <div className="mt-3">
              <p className="text-xs uppercase tracking-widest text-ink-muted mb-1">Reclassification factors</p>
              <ul className="space-y-1">
                {draft.cvd_risk.reclassification_factors.map((f, i) => (
                  <li key={i} className="text-sm text-ink">▸ {f}</li>
                ))}
              </ul>
            </div>
          )}
        </Section>
      )}

      {/* Clinical patterns */}
      {draft.clinical_patterns?.length > 0 && (
        <Section title="§ 05  Clinical Patterns">
          {draft.clinical_patterns.map((p, i) => (
            <div key={i} className="mb-3 last:mb-0">
              <p className="text-sm font-semibold text-ink">{p.name}</p>
              <p className="text-sm text-ink-sub">{p.evidence}</p>
            </div>
          ))}
        </Section>
      )}

      {/* Further investigations */}
      {draft.further_investigations?.length > 0 && (
        <Section title="§ 06  Further Investigations">
          <ul className="space-y-1">
            {draft.further_investigations.map((item, i) => (
              <li key={i} className="text-sm text-ink">
                ▸ {typeof item === "string" ? item : (item as { investigation?: string }).investigation}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Management suggestions */}
      {draft.management_suggestions?.length > 0 && (
        <Section title="§ 07  Management Suggestions">
          <ul className="space-y-1">
            {draft.management_suggestions.map((item, i) => (
              <li key={i} className="text-sm text-ink">
                ▸ {typeof item === "string" ? item : (item as { suggestion?: string }).suggestion}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Action plan */}
      {draft.action_plan && (
        <Section title="§ 08  Action Plan">
          {(["diet", "exercise", "sleep", "alcohol"] as const).map((key) =>
            draft.action_plan[key] ? (
              <div key={key} className="mb-3 last:mb-0">
                <p className="text-xs uppercase tracking-widest text-ink-muted mb-1">{key}</p>
                <p className="text-sm text-ink">{draft.action_plan[key]}</p>
              </div>
            ) : null
          )}
        </Section>
      )}

      {/* Follow-up plan */}
      {draft.follow_up_plan && (
        <Section title="§ 09  Follow-Up Plan">
          {draft.follow_up_plan.repeat_tests?.length > 0 && (
            <div className="mb-3">
              <p className="text-xs uppercase tracking-widest text-ink-muted mb-1">Repeat Tests</p>
              <ul className="space-y-1">
                {draft.follow_up_plan.repeat_tests.map((t, i) => (
                  <li key={i} className="text-sm text-ink">▸ {t}</li>
                ))}
              </ul>
            </div>
          )}
          {draft.follow_up_plan.red_flags?.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-widest text-red-700 mb-1">Red Flags — Call 1990</p>
              <ul className="space-y-1">
                {draft.follow_up_plan.red_flags.map((f, i) => (
                  <li key={i} className="text-sm text-red-800">▸ {f}</li>
                ))}
              </ul>
            </div>
          )}
        </Section>
      )}

      {/* Patient summary */}
      {draft.patient_summary && (
        <div className="bg-accent-light border-l-4 border-accent rounded-r-xl p-4">
          <p className="text-xs uppercase tracking-widest text-accent-dark mb-2">§ 10  Patient Summary</p>
          <p className="text-sm text-ink leading-relaxed">{draft.patient_summary}</p>
        </div>
      )}

      {/* Doctor notes */}
      <div>
        <label className="block text-xs uppercase tracking-widest text-ink-muted mb-1">
          Clinician&apos;s Notes (optional)
        </label>
        <textarea
          value={doctorNotes}
          onChange={(e) => setDoctorNotes(e.target.value)}
          rows={4}
          placeholder="Add any additional notes or amendments…"
          className="w-full rounded-xl border border-rule bg-white px-4 py-3 text-sm text-ink placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-accent resize-none"
        />
      </div>

      <button
        onClick={() => onConfirm(doctorNotes)}
        disabled={confirming}
        className="w-full py-3.5 bg-accent text-white font-medium rounded-xl disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {confirming ? (
          <>
            <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Generating PDF…
          </>
        ) : "Generate PDF Report"}
      </button>
    </div>
  );
}
