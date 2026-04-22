"use client";
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, X, CheckCircle, Loader2 } from "lucide-react";
import { uploadFile } from "@/lib/api";

export interface LabInputData {
  labText: string;
  uploadIds: string[];
  uploadedFiles: { name: string; id: string; preview: string }[];
}

interface Props {
  data: LabInputData;
  onChange: (d: LabInputData) => void;
  onNext: () => void;
}

type Tab = "upload" | "paste";

export default function Step1LabInput({ data, onChange, onNext }: Props) {
  const [tab, setTab] = useState<Tab>("upload");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const onDrop = useCallback(async (accepted: File[]) => {
    if (!accepted.length) return;
    setUploading(true);
    setError("");
    try {
      const results = await Promise.all(accepted.map(uploadFile));
      const newFiles = results.map((r, i) => ({
        id: r.upload_id,
        name: accepted[i].name,
        preview: r.extracted_text.slice(0, 120) + (r.extracted_text.length > 120 ? "…" : ""),
      }));
      onChange({
        ...data,
        uploadIds: [...data.uploadIds, ...results.map((r) => r.upload_id)],
        uploadedFiles: [...data.uploadedFiles, ...newFiles],
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [data, onChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "image/*": [".jpg", ".jpeg", ".png", ".webp"] },
    multiple: true,
  });

  const removeFile = (id: string) => {
    onChange({
      ...data,
      uploadIds: data.uploadIds.filter((u) => u !== id),
      uploadedFiles: data.uploadedFiles.filter((f) => f.id !== id),
    });
  };

  const canProceed = data.uploadIds.length > 0 || data.labText.trim().length > 20;

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-2xl font-serif text-ink">Lab Results</h2>
        <p className="text-sm text-ink-sub mt-1">Upload a file or paste the lab text directly.</p>
      </div>

      {/* Tab switcher */}
      <div className="flex rounded-lg border border-rule overflow-hidden">
        {(["upload", "paste"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 py-2.5 text-sm font-medium transition-colors
              ${tab === t ? "bg-accent text-white" : "bg-white text-ink-sub hover:bg-paper-alt"}`}
          >
            {t === "upload" ? "Upload File" : "Paste Text"}
          </button>
        ))}
      </div>

      {tab === "upload" && (
        <div className="space-y-3">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
              ${isDragActive ? "border-accent bg-accent-light" : "border-rule bg-white hover:border-accent-dark"}`}
          >
            <input {...getInputProps()} />
            {uploading ? (
              <div className="flex flex-col items-center gap-2 text-ink-sub">
                <Loader2 size={28} className="animate-spin text-accent" />
                <p className="text-sm">Uploading…</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2 text-ink-muted">
                <Upload size={28} />
                <p className="text-sm font-medium text-ink-sub">
                  {isDragActive ? "Drop here" : "Tap to upload or drag & drop"}
                </p>
                <p className="text-xs">PDF, JPG, PNG, WEBP</p>
              </div>
            )}
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          {data.uploadedFiles.map((f) => (
            <div key={f.id} className="flex items-start gap-3 p-3 bg-white rounded-xl border border-rule">
              <CheckCircle size={18} className="text-green-600 shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-ink truncate">{f.name}</p>
                <p className="text-xs text-ink-muted mt-0.5 line-clamp-2 font-mono">{f.preview}</p>
              </div>
              <button onClick={() => removeFile(f.id)} className="text-ink-muted hover:text-red-600 shrink-0">
                <X size={16} />
              </button>
            </div>
          ))}
        </div>
      )}

      {tab === "paste" && (
        <div className="space-y-2">
          <label className="text-xs uppercase tracking-widest text-ink-muted">
            Lab Report Text
          </label>
          <textarea
            value={data.labText}
            onChange={(e) => onChange({ ...data, labText: e.target.value })}
            placeholder={"Paste your lab results here…\n\nExample:\nHaemoglobin  12.5 g/dL  [13.0–17.0]\nPlatelets  220 ×10⁹/L  [150–400]"}
            rows={12}
            className="w-full rounded-xl border border-rule bg-white px-4 py-3 text-sm font-mono text-ink placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-accent resize-none"
          />
        </div>
      )}

      <button
        disabled={!canProceed}
        onClick={onNext}
        className="w-full py-3.5 bg-accent text-white font-medium rounded-xl disabled:opacity-40 transition-opacity"
      >
        Continue to Patient Details
      </button>
    </div>
  );
}
