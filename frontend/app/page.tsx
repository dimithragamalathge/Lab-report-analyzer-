import Link from "next/link";
import Header from "@/components/layout/Header";
import BottomNav from "@/components/layout/BottomNav";
import RecentReports from "@/components/reports/RecentReports";

export default function DashboardPage() {
  return (
    <>
      <Header />
      <main className="max-w-2xl mx-auto px-4 pt-6 pb-28">
        {/* Hero */}
        <div className="mb-8">
          <p className="text-xs tracking-widest uppercase text-ink-muted mb-1">
            Clinical Lab Analysis
          </p>
          <h1 className="font-serif text-3xl text-ink leading-snug">
            Good morning,<br />
            <span className="text-accent italic">Dr. Gamalathge</span>
          </h1>
        </div>

        {/* Quick action */}
        <Link
          href="/analyze"
          className="block w-full py-4 px-6 bg-accent text-white rounded-xl text-center font-medium text-base active:opacity-80 transition-opacity mb-8 shadow-sm"
        >
          + Analyse New Lab Report
        </Link>

        {/* Recent reports */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold tracking-wide uppercase text-ink-sub">
              Recent Reports
            </h2>
            <Link href="/reports" className="text-xs text-accent underline">
              View all
            </Link>
          </div>
          <RecentReports />
        </section>
      </main>
      <BottomNav />
    </>
  );
}
