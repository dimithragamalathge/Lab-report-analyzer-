"use client";
import { ChevronLeft } from "lucide-react";

const STEPS = ["Lab Input", "Patient", "Analysing", "Review", "Done"];

interface Props {
  step: number;          // 1-based
  onBack?: () => void;
  children: React.ReactNode;
}

export default function WizardShell({ step, onBack, children }: Props) {
  return (
    <div className="min-h-screen bg-paper flex flex-col">
      {/* Top bar */}
      <div className="sticky top-0 z-40 bg-paper border-b border-rule">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center gap-3">
          {onBack && step > 1 && step < 5 ? (
            <button onClick={onBack} className="p-1 -ml-1 text-ink-muted">
              <ChevronLeft size={22} />
            </button>
          ) : (
            <div className="w-7" />
          )}
          <div className="flex-1">
            <p className="text-xs text-ink-muted mb-1">
              Step {step} of {STEPS.length}
            </p>
            {/* Progress bar */}
            <div className="h-1 bg-rule rounded-full overflow-hidden">
              <div
                className="h-full bg-accent rounded-full transition-all duration-300"
                style={{ width: `${(step / STEPS.length) * 100}%` }}
              />
            </div>
          </div>
          <span className="text-xs font-medium text-ink-sub w-20 text-right">
            {STEPS[step - 1]}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 max-w-2xl w-full mx-auto px-4 py-6 pb-10">
        {children}
      </div>
    </div>
  );
}
