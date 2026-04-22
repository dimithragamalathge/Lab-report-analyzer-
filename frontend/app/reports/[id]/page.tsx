"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, Download, Trash2 } from "lucide-react";
import Header from "@/components/layout/Header";
import BottomNav from "@/components/layout/BottomNav";
import { getReport, deleteReport, pdfUrl } from "@/lib/api";
import type { ReportDetail } from "@/lib/types";

export default function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getReport(id)
      .then(setReport)
      .catch(() => router.push("/reports"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    if (!confirm("Delete this report permanently?")) return;
    await deleteReport(id);
    router.push("/reports");
  };

  if (loading) {
    return (
      <>
        <Header />
        <main className="max-w-2xl mx-auto px-4 pt-6 pb-28 space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 rounded-xl bg-paper-alt animate-pulse" />
          ))}
        </main>
      </>
    );
  }

  if (!report) return null;

  const date = new Date(report.created_at).toLocaleDateString("en-GB", {
    day: "numeric", month: "long", year: "numeric",
  });

  return (
    <>
      <Header />
      <main className="max-w-2xl mx-auto px-4 pt-4 pb-28 space-y-5">
        {/* Back + actions */}
        <div className="flex items-center justify-between">
          <Link href="/reports" className="flex items-center gap-1 text-sm text-ink-muted">
            <ChevronLeft size={16} /> Back
          </Link>
          <div className="flex gap-2">
            {report.pdf_url && (
              <a
                href={pdfUrl(report.id)}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 px-3 py-1.5 bg-accent text-white text-xs rounded-lg"
              >
                <Download size={14} /> PDF
              </a>
            )}
            <button
              onClick={handleDelete}
              className="flex items-center gap-1 px-3 py-1.5 bg-red-100 text-red-700 text-xs rounded-lg"
            >
              <Trash2 size={14} /> Delete
            </button>
          </div>
        </div>

        {/* Patient card */}
        <div className="bg-white rounded-xl border border-rule p-4">
          <p className="text-xs text-ink-muted uppercase tracking-widest mb-1">Patient</p>
          <p className="text-xl font-serif italic text-ink">{report.patient_name}</p>
          <p className="text-sm text-ink-sub mt-1">
            {[report.patient_age && `${report.patient_age} yrs`,
              report.patient_sex,
              report.patient_dob,
            ].filter(Boolean).join(" · ")}
          </p>
          <p className="text-xs text-ink-muted mt-2">{date}</p>
        </div>

        {/* Critical values */}
        {report.critical_values?.length > 0 && (
          <div className="bg-[#5a2418] text-white rounded-xl p-4">
            <p className="text-xs font-bold tracking-widest uppercase mb-2">
              Critical Values — Immediate Review
            </p>
            {report.critical_values.map((cv, i) => (
              <p key={i} className="text-sm font-mono">
                {cv.analyte}: {cv.result} {cv.unit} {cv.note && `— ${cv.note}`}
              </p>
            ))}
          </div>
        )}

        {/* Key findings */}
        {report.clinical_patterns?.length > 0 && (
          <Section title="Clinical Patterns">
            {report.clinical_patterns.map((p, i) => (
              <div key={i} className="mb-3">
                <p className="text-sm font-semibold text-ink">{p.name}</p>
                <p className="text-sm text-ink-sub">{p.evidence}</p>
              </div>
            ))}
          </Section>
        )}

        {/* CVD risk */}
        {report.cvd_risk_result?.risk_category && (
          <Section title="CVD Risk — WHO SEAR-B (10-yr)">
            <div className="flex items-center gap-4">
              <div>
                <p className="text-3xl font-bold text-accent">
                  {report.cvd_risk_result.risk_percent_10yr}%
                </p>
                <p className="text-sm text-ink-sub">{report.cvd_risk_result.risk_category}</p>
              </div>
              <div className="text-sm text-ink-sub">
                <p>NICE NG238 threshold {report.cvd_risk_result.treatment_threshold_met ? "met ✓" : "not met"}</p>
                <p className="text-xs text-ink-muted mt-1">
                  South Asian 1.4× calibration applied
                </p>
              </div>
            </div>
          </Section>
        )}

        {/* Patient summary */}
        {report.patient_summary && (
          <div className="bg-accent-light border-l-4 border-accent rounded-r-xl p-4">
            <p className="text-xs uppercase tracking-widest text-accent-dark mb-2">
              Patient Summary
            </p>
            <p className="text-sm text-ink leading-relaxed">{report.patient_summary}</p>
          </div>
        )}

        {/* Further investigations */}
        {report.further_investigations?.length > 0 && (
          <Section title="Further Investigations">
            <ul className="space-y-1">
              {report.further_investigations.map((item, i) => (
                <li key={i} className="text-sm text-ink">▸ {typeof item === "string" ? item : (item as { investigation?: string }).investigation}</li>
              ))}
            </ul>
          </Section>
        )}

        {/* Management */}
        {report.management_suggestions?.length > 0 && (
          <Section title="Management Suggestions">
            <ul className="space-y-1">
              {report.management_suggestions.map((item, i) => (
                <li key={i} className="text-sm text-ink">▸ {typeof item === "string" ? item : (item as { suggestion?: string }).suggestion}</li>
              ))}
            </ul>
          </Section>
        )}

        {/* Download PDF */}
        {report.pdf_url && (
          <a
            href={pdfUrl(report.id)}
            target="_blank"
            rel="noreferrer"
            className="block w-full py-3 text-center bg-accent text-white font-medium rounded-xl"
          >
            Download Full PDF Report
          </a>
        )}
      </main>
      <BottomNav />
    </>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-rule p-4">
      <p className="text-xs uppercase tracking-widest text-ink-muted mb-3">{title}</p>
      {children}
    </div>
  );
}
