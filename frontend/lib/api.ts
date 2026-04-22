import type { DraftResponse, ReportDetail, ReportSummary } from "./types";

const BASE = "/api";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

// Upload

export async function uploadFile(file: File): Promise<{ upload_id: string; filename: string; file_type: string; extracted_text: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Upload failed");
  }
  return res.json();
}

// Analyze

export interface AnalyzeStartPayload {
  lab_text?: string;
  upload_ids?: string[];
  patient: Record<string, unknown>;
  cvd_factors?: Record<string, unknown>;
  report_settings?: { report_date?: string };
}

export async function analyzeStart(payload: AnalyzeStartPayload): Promise<{ report_id: string; draft: DraftResponse }> {
  return req("/analyze/start", { method: "POST", body: JSON.stringify(payload) });
}

export async function analyzeConfirm(report_id: string, doctor_edits?: string): Promise<{ report_id: string; pdf_url: string; status: string }> {
  return req("/analyze/confirm", { method: "POST", body: JSON.stringify({ report_id, doctor_edits }) });
}

// Reports

export async function listReports(page = 1, limit = 20): Promise<{ reports: ReportSummary[]; total: number }> {
  return req(`/reports?page=${page}&limit=${limit}`);
}

export async function getReport(id: string): Promise<ReportDetail> {
  return req(`/reports/${id}`);
}

export async function deleteReport(id: string): Promise<{ success: boolean }> {
  return req(`/reports/${id}`, { method: "DELETE" });
}

export function pdfUrl(id: string): string {
  return `${BASE}/reports/${id}/pdf`;
}

// Health

export async function healthCheck(): Promise<{ status: string }> {
  return req("/health");
}
