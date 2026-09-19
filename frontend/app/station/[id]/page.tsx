"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { VitalsStrip } from "@/components/VitalsStrip";
import { api } from "@/lib/api";
import type { VisibleCase } from "@/lib/types";

export default function StationBriefPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [item, setItem] = useState<VisibleCase | null>(null);
  const [error, setError] = useState("");
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    api
      .getCase(params.id)
      .then(setItem)
      .catch(() => setError("This station brief could not be loaded."));
  }, [params.id]);

  async function startInterview() {
    if (!item) return;
    setStarting(true);
    try {
      const session = await api.startSession(item.id);
      router.push(`/station/${item.id}/interview?session=${session.session.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start the station");
      setStarting(false);
    }
  }

  if (error && !item) {
    return <p className="text-rust">{error}</p>;
  }

  if (!item) {
    return <p className="text-ink-muted">Preparing station brief…</p>;
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link href="/" className="text-sm text-clinic-dark hover:underline">
        ← Back to circuit
      </Link>
      <section className="rounded-3xl border border-black/10 bg-paper-card p-8 shadow-station">
        <p className="text-xs uppercase tracking-[0.28em] text-ink-muted">Candidate instructions</p>
        <h1 className="mt-2 font-serif text-4xl">{item.title}</h1>
        <p className="mt-3 text-clinic-dark">
          {item.age}-year-old {item.gender.toLowerCase()} · {item.setting}
        </p>
        <p className="mt-6 text-lg leading-8">{item.brief_history}</p>
        <p className="mt-4 font-medium">Presenting complaint: {item.presenting_complaint}</p>
        <div className="mt-6">
          <VitalsStrip vitals={item.vitals} />
        </div>
        <ol className="mt-8 list-decimal space-y-2 pl-5 text-sm leading-6 text-ink-muted">
          <li>Take a focused history from the standardized patient.</li>
          <li>Do not expect the patient to know labs, imaging, or a diagnosis.</li>
          <li>When finished, submit your top 3 differentials and next steps.</li>
        </ol>
        {error && <p className="mt-4 text-sm text-rust">{error}</p>}
        <button
          onClick={startInterview}
          disabled={starting}
          className="mt-8 rounded-full bg-clinic px-6 py-3 text-sm font-medium text-white hover:bg-clinic-dark disabled:opacity-60"
        >
          {starting ? "Opening interview…" : "Knock and enter"}
        </button>
      </section>
    </div>
  );
}
