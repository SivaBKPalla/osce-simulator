"use client";

import { useState } from "react";
import type { AnalysisTab } from "@/lib/types";

export function AnalysisTabs({ tabs }: { tabs: AnalysisTab[] }) {
  const [active, setActive] = useState(tabs[0]?.id ?? "yours");
  const current = tabs.find((tab) => tab.id === active) ?? tabs[0];
  if (!current) return null;

  return (
    <div className="mt-4">
      <div className="flex flex-wrap gap-2 border-b border-black/10 pb-2">
        {tabs.map((tab) => {
          const selected = tab.id === current.id;
          return (
            <button
              key={tab.id}
              type="button"
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
      <div className="mt-3 space-y-2 text-sm leading-6">
        <p>{current.body}</p>
        {current.bullets.length > 0 && (
          <ul className="list-disc space-y-1 pl-5 text-ink-muted">
            {current.bullets.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
