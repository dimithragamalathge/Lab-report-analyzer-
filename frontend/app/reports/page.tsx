"use client";
import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import BottomNav from "@/components/layout/BottomNav";
import ReportCard from "@/components/reports/ReportCard";
import { listReports, deleteReport } from "@/lib/api";
import type { ReportSummary } from "@/lib/types";

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const LIMIT = 20;

  const load = (p: number) => {
    setLoading(true);
    listReports(p, LIMIT)
      .then((r) => { setReports(r.reports); setTotal(r.total); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(page); }, [page]);

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this report?")) return;
    await deleteReport(id);
    load(page);
  };

  return (
    <>
      <Header />
      <main className="max-w-2xl mx-auto px-4 pt-6 pb-28">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-semibold text-ink">Report History</h1>
          {total > 0 && (
            <span className="text-xs text-ink-muted">{total} total</span>
          )}
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 rounded-xl bg-paper-alt animate-pulse" />
            ))}
          </div>
        ) : reports.length === 0 ? (
          <p className="text-sm text-ink-muted text-center py-16">No reports found.</p>
        ) : (
          <div className="space-y-3">
            {reports.map((r) => (
              <div key={r.id} className="relative group">
                <ReportCard report={r} />
                <button
                  onClick={() => handleDelete(r.id)}
                  className="absolute top-3 right-10 hidden group-hover:flex items-center justify-center w-7 h-7 rounded-full bg-red-100 text-red-600 text-xs hover:bg-red-200 transition-colors"
                  title="Delete"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > LIMIT && (
          <div className="flex justify-center gap-3 mt-6">
            <button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className="px-4 py-2 text-sm rounded-lg border border-rule disabled:opacity-40"
            >
              Previous
            </button>
            <span className="self-center text-sm text-ink-muted">
              Page {page} of {Math.ceil(total / LIMIT)}
            </span>
            <button
              disabled={page >= Math.ceil(total / LIMIT)}
              onClick={() => setPage(page + 1)}
              className="px-4 py-2 text-sm rounded-lg border border-rule disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}
      </main>
      <BottomNav />
    </>
  );
}
