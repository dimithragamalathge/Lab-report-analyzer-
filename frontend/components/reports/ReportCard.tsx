import Link from "next/link";
import { FileText, ChevronRight } from "lucide-react";
import type { ReportSummary } from "@/lib/types";

const STATUS_STYLES: Record<string, string> = {
  completed: "bg-green-100 text-green-800",
  draft:     "bg-amber-100 text-amber-800",
  analyzing: "bg-blue-100 text-blue-800",
  error:     "bg-red-100 text-red-800",
};

export default function ReportCard({ report }: { report: ReportSummary }) {
  const date = new Date(report.created_at).toLocaleDateString("en-GB", {
    day: "numeric", month: "short", year: "numeric",
  });
  const statusStyle = STATUS_STYLES[report.status] ?? "bg-paper-alt text-ink-sub";

  return (
    <Link
      href={`/reports/${report.id}`}
      className="flex items-center gap-3 p-4 bg-white rounded-xl border border-rule active:bg-paper-alt transition-colors"
    >
      <div className="w-10 h-10 rounded-lg bg-accent-light flex items-center justify-center shrink-0">
        <FileText size={18} className="text-accent" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-ink text-sm truncate">
          {report.patient_name}
        </p>
        <p className="text-xs text-ink-muted mt-0.5">
          {date}
          {report.patient_age ? ` · ${report.patient_age} yrs` : ""}
          {report.patient_sex ? ` · ${report.patient_sex}` : ""}
        </p>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${statusStyle}`}>
          {report.status}
        </span>
        <ChevronRight size={16} className="text-ink-muted" />
      </div>
    </Link>
  );
}
