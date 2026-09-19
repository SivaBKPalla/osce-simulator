import Link from "next/link";
import type { VisibleCase } from "@/lib/types";

export function CaseCard({ item, index }: { item: VisibleCase; index: number }) {
  return (
    <article className="flex h-full flex-col rounded-2xl border border-black/10 bg-paper-card p-5 shadow-station">
      <div className="mb-4 flex items-center justify-between">
        <span className="rounded-full bg-ink px-2.5 py-1 text-[11px] uppercase tracking-[0.16em] text-paper">
          Station {String(index + 1).padStart(2, "0")}
        </span>
        <span className="text-sm text-ink-muted">
          {item.age} · {item.gender}
        </span>
      </div>
      <h3 className="font-serif text-2xl leading-tight">{item.title}</h3>
      <p className="mt-2 text-sm text-clinic-dark">{item.presenting_complaint}</p>
      <p className="mt-4 flex-1 text-sm leading-6 text-ink-muted">{item.brief_history}</p>
      <p className="mt-4 text-xs uppercase tracking-[0.16em] text-ink-muted">{item.setting}</p>
      <Link
        href={`/station/${item.id}`}
        className="mt-5 inline-flex items-center justify-center rounded-full bg-clinic px-4 py-2.5 text-sm font-medium text-white hover:bg-clinic-dark"
      >
        Enter station
      </Link>
    </article>
  );
}
