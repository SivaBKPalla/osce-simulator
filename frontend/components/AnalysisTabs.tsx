"use client";

import { useMemo, useState } from "react";
import type { AnalysisTab } from "@/lib/types";

function tabId(tab: AnalysisTab, index: number) {
  const label = tab.label.toLowerCase();
  if (label.includes("your")) return "yours";
  if (label.includes("model")) return "model";
  if (label.includes("why")) return "why";
  const raw = (tab.id || `tab-${index}`).toLowerCase().replace(/\s+/g, "-");
  return raw || `tab-${index}`;
}

export function AnalysisTabs({ tabs }: { tabs: AnalysisTab[] }) {
  const items = useMemo(() => {
    const seen = new Set<string>();
    return tabs.map((tab, index) => {
      let id = tabId(tab, index);
      if (seen.has(id)) {
        id = `${id}-${index}`;
      }
      seen.add(id);
      return { ...tab, id };
    });
  }, [tabs]);

  const [active, setActive] = useState(items[0]?.id ?? "yours");
  const current = items.find((tab) => tab.id === active) ?? items[0];
  if (!current) return null;

  return (
    <div className="mt-4">
      <div role="tablist" className="flex flex-wrap gap-2 border-b border-black/10 pb-2">
        {items.map((tab) => {
          const selected = tab.id === current.id;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => setActive(tab.id)}
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                selected ? "bg-ink text-paper" : "bg-black/5 text-ink-muted hover:bg-black/10"
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
      <div key={current.id} role="tabpanel" className="mt-3 space-y-2 overflow-hidden text-sm leading-6">
        {current.body ? <p>{current.body}</p> : null}
        {current.bullets.length > 0 && (
          <ul className="list-disc space-y-1 pl-5 text-ink-muted">
            {current.bullets.map((item, index) => (
              <li key={`${current.id}-bullet-${index}`}>{item}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
