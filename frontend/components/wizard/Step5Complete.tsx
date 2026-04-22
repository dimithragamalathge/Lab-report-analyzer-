"use client";
import Link from "next/link";
import { CheckCircle, Download, ArrowRight } from "lucide-react";
import { pdfUrl } from "@/lib/api";

interface Props {
  reportId: string;
}

export default function Step5Complete({ reportId }: Props) {
  return (
    <div className="flex flex-col items-center text-center gap-6 pt-12">
      <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center">
        <CheckCircle size={40} className="text-green-600" />
      </div>

      <div>
        <h2 className="text-2xl font-serif text-ink">Report Complete</h2>
        <p className="text-sm text-ink-sub mt-2">
          Your PDF report has been generated and saved.
        </p>
      </div>

      <div className="w-full space-y-3">
        <a
          href={pdfUrl(reportId)}
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-center gap-2 w-full py-3.5 bg-accent text-white font-medium rounded-xl"
        >
          <Download size={18} />
          Download PDF Report
        </a>

        <Link
          href={`/reports/${reportId}`}
          className="flex items-center justify-center gap-2 w-full py-3.5 bg-white border border-rule text-ink font-medium rounded-xl"
        >
          View Report Detail
          <ArrowRight size={16} />
        </Link>

        <Link
          href="/analyze"
          className="flex items-center justify-center gap-2 w-full py-3 text-sm text-ink-sub"
        >
          Analyse another report
        </Link>
      </div>
    </div>
  );
}
