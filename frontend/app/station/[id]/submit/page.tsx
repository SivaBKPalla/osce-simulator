"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { AnalysisTabs } from "@/components/AnalysisTabs";
import { api } from "@/lib/api";
import type { EvaluationResult, VisibleCase } from "@/lib/types";

export default function SubmitPage() {
  return (
    <Suspense fallback={<p className="text-ink-muted">Opening examiner desk…</p>}>
      <SubmitClient />
    </Suspense>
  );
}

function SubmitClient() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");
  const [item, setItem] = useState<VisibleCase | null>(null);
  const [d1, setD1] = useState("");
  const [d2, setD2] = useState("");
  const [d3, setD3] = useState("");
  const [nextSteps, setNextSteps] = useState("");
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!sessionId) return;
    api
      .getSession(sessionId)
      .then((data) => setItem(data.case))
      .catch(() => setError("Could not load this session."));
  }, [sessionId]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!sessionId) {
      setError("Missing session id.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const evaluation = await api.evaluate(sessionId, {
        differential_1: d1,
        differential_2: d2,
        differential_3: d3,
        next_steps: nextSteps,
      });
      setResult(evaluation);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link
        href={`/station/${params.id}/interview?session=${sessionId ?? ""}`}
        className="text-sm text-clinic-dark hover:underline"
      >
        ← Return to interview
      </Link>
      <section className="rounded-3xl border border-black/10 bg-paper-card p-8 shadow-station">
        <p className="text-xs uppercase tracking-[0.28em] text-ink-muted">Examiner desk</p>
        <h1 className="mt-2 font-serif text-4xl">Differentials and next steps</h1>
        <p className="mt-3 text-ink-muted">
          {item
            ? `${item.age}-year-old ${item.gender.toLowerCase()} with ${item.presenting_complaint.toLowerCase()}.`
            : "Commit to a working assessment before you leave the station."}
        </p>

        {!result ? (
          <form onSubmit={onSubmit} className="mt-8 space-y-4">
            <Field label="Most likely" value={d1} onChange={setD1} />
            <Field label="Second" value={d2} onChange={setD2} />
            <Field label="Third / must-not-miss" value={d3} onChange={setD3} />
            <label className="block text-sm">
              Proposed next steps
              <textarea
                required
                rows={5}
                value={nextSteps}
                onChange={(event) => setNextSteps(event.target.value)}
                placeholder="Investigations, immediate management, consults…"
                className="mt-1 w-full rounded-lg border border-black/10 bg-white px-3 py-2 outline-none ring-clinic/30 focus:ring"
              />
            </label>
            {error && <p className="text-sm text-rust">{error}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="rounded-full bg-clinic px-6 py-3 text-sm font-medium text-white hover:bg-clinic-dark disabled:opacity-60"
            >
              {submitting ? "Scoring rubric…" : "Submit for examiner feedback"}
            </button>
          </form>
        ) : (
          <div className="mt-8 space-y-6">
            <div className="rounded-2xl bg-ink px-5 py-4 text-paper">
              <p className="text-xs uppercase tracking-[0.2em] text-paper/60">Overall</p>
              <p className="font-serif text-4xl">
                {result.overall_score}
                <span className="text-xl text-paper/60"> / {result.max_score}</span>
              </p>
              <p className="mt-2 text-sm text-paper/80">{result.summary}</p>
              <div className="mt-4 rounded-xl bg-white/10 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-paper/60">
                  {result.diagnosis_match === "exact" || result.diagnosis_correct
                    ? "Diagnosis matched"
                    : result.diagnosis_match === "related"
                      ? "Related — half credit"
                      : "Correct diagnosis"}
                </p>
                <p className="mt-1 font-medium text-clinic-soft">{result.hidden_diagnosis}</p>
                {result.diagnosis_explanation && (
                  <p className="mt-2 text-sm text-paper/80">{result.diagnosis_explanation}</p>
                )}
              </div>
            </div>
            <div className="space-y-3">
              {result.rubric.map((row, index) => (
                <article key={`${row.criterion}-${index}`} className="rounded-xl border border-black/10 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <h2 className="font-medium">{row.criterion}</h2>
                    <p className="tabular-nums text-sm">
                      {row.score}/{row.max_score}
                    </p>
                  </div>
                  <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-black/10">
                    <div
                      className="h-full bg-clinic"
                      style={{ width: `${(row.score / row.max_score) * 100}%` }}
                    />
                  </div>
                  <p className="mt-2 text-sm text-ink-muted">{row.comments}</p>
                  {row.tabs && row.tabs.length > 0 && (
                    <AnalysisTabs key={`${row.criterion}-${index}-tabs`} tabs={row.tabs} />
                  )}
                </article>
              ))}
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              <NoteList title="Strengths" items={result.strengths} />
              <NoteList title="Missed questions" items={result.missed_questions} />
              <NoteList title="Study next" items={result.next_study_focus} />
            </div>
            <Link href="/" className="inline-block text-sm text-clinic-dark hover:underline">
              Return to circuit board
            </Link>
          </div>
        )}
      </section>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block text-sm">
      {label}
      <input
        required
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-1 w-full rounded-lg border border-black/10 bg-white px-3 py-2 outline-none ring-clinic/30 focus:ring"
      />
    </label>
  );
}

function NoteList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-xl bg-clinic-soft/40 p-4">
      <h3 className="text-xs uppercase tracking-[0.16em] text-clinic-dark">{title}</h3>
      <ul className="mt-2 list-disc space-y-1 pl-4 text-sm">
        {items.length === 0 ? (
          <li>None noted</li>
        ) : (
          items.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)
        )}
      </ul>
    </div>
  );
}
