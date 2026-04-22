"use client";
import { useEffect, useState } from "react";
import { listReports } from "@/lib/api";
import type { ReportSummary } from "@/lib/types";
import ReportCard from "./ReportCard";

export default function RecentReports() {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listReports(1, 5)
      .then((r) => setReports(r.reports))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 rounded-xl bg-paper-alt animate-pulse" />
        ))}
      </div>
    );
  }

  if (reports.length === 0) {
    return (
      <p className="text-sm text-ink-muted text-center py-8">
        No reports yet. Analyse your first lab report above.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {reports.map((r) => (
        <ReportCard key={r.id} report={r} />
      ))}
    </div>
  );
}
