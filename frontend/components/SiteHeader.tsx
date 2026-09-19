"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { href: "/", label: "Circuit" },
  { href: "/about", label: "About Me" },
  { href: "/coffee", label: "Buy me a coffee" },
];

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="border-b border-black/10 bg-ink text-paper">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <Link href="/" className="shrink-0">
          <p className="text-[11px] uppercase tracking-[0.28em] text-clinic-soft/80">
            Clinical Skills Centre
          </p>
          <p className="font-serif text-xl tracking-tight">OSCE Station Simulator</p>
        </Link>
        <nav aria-label="Primary" className="flex flex-wrap items-end gap-1">
          {tabs.map((tab) => {
            const active = tab.href === "/" ? pathname === "/" : pathname.startsWith(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`rounded-t-lg px-3 py-2 text-sm transition ${
                  active
                    ? "bg-paper text-ink"
                    : "text-paper/75 hover:bg-white/10 hover:text-paper"
                }`}
              >
                {tab.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
