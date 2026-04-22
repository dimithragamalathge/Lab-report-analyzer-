"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, FileText, Plus } from "lucide-react";

const links = [
  { href: "/",        label: "Home",    Icon: Home },
  { href: "/analyze", label: "Analyze", Icon: Plus },
  { href: "/reports", label: "History", Icon: FileText },
];

export default function BottomNav() {
  const path = usePathname();

  return (
    <nav className="fixed bottom-0 inset-x-0 z-40 bg-paper border-t border-rule pb-safe">
      <div className="max-w-2xl mx-auto flex">
        {links.map(({ href, label, Icon }) => {
          const active = href === "/" ? path === "/" : path.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex-1 flex flex-col items-center justify-center gap-1 py-3 text-xs transition-colors
                ${active ? "text-accent" : "text-ink-muted"}`}
            >
              <Icon size={20} strokeWidth={active ? 2.5 : 1.8} />
              <span>{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
