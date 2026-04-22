"use client";
import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

const STAGES = [
  "Reading lab values…",
  "Analysing clinical patterns…",
  "Calculating CVD risk (WHO SEAR-B)…",
  "Preparing draft report…",
];

export default function Step3Analyzing() {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setStage((s) => (s < STAGES.length - 1 ? s + 1 : s));
    }, 2800);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-8 text-center">
      <Loader2 size={48} className="text-accent animate-spin" />
      <div>
        <h2 className="text-xl font-serif text-ink mb-2">Analysing…</h2>
        <p className="text-sm text-ink-sub transition-all duration-500">{STAGES[stage]}</p>
      </div>
      <div className="flex gap-2">
        {STAGES.map((_, i) => (
          <div
            key={i}
            className={`w-2 h-2 rounded-full transition-colors duration-300
              ${i <= stage ? "bg-accent" : "bg-rule"}`}
          />
        ))}
      </div>
    </div>
  );
}
