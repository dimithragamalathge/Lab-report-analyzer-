"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
  const path = usePathname();

  const isAnalyze = path.startsWith("/analyze");

  return (
    <header className="sticky top-0 z-40 bg-paper border-b border-rule">
      <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="font-serif text-lg font-bold text-ink leading-none">
            Gamalathge
          </span>
          <span className="text-xs text-ink-muted tracking-widest uppercase">
            Healthcare
          </span>
        </Link>

        {!isAnalyze && (
          <Link
            href="/analyze"
            className="px-4 py-2 bg-accent text-white text-sm font-medium rounded-lg active:opacity-80 transition-opacity"
          >
            New Report
          </Link>
        )}
      </div>
    </header>
  );
}
