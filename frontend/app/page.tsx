"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CaseCard } from "@/components/CaseCard";
import { api } from "@/lib/api";
import { clearCircuitCache, loadCircuit } from "@/lib/circuit";
import type { VisibleCase } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();
  const [cases, setCases] = useState<VisibleCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [complaint, setComplaint] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [llmMode, setLlmMode] = useState("mock");

  useEffect(() => {
    let cancelled = false;
    let settled = false;

    async function loadBoard() {
      try {
        const [items, health] = await Promise.all([
          loadCircuit(),
          api.health().catch(() => ({ llm: "offline" })),
        ]);
        if (cancelled) return;
        setCases(items);
        setLlmMode(health.llm);
        setError("");
      } catch {
        if (!cancelled) {
          setError("Could not load stations. Tap Deal a new circuit to try again.");
        }
      } finally {
        settled = true;
        if (!cancelled) setLoading(false);
      }
    }

    const watchdog = window.setTimeout(() => {
      if (!cancelled && !settled) {
        setLoading(false);
        setError("Could not load stations. Tap Deal a new circuit to try again.");
      }
    }, 60_000);

    void loadBoard();
    return () => {
      cancelled = true;
      window.clearTimeout(watchdog);
    };
  }, []);

  async function refreshCircuit() {
    setRefreshing(true);
    setError("");
    try {
      clearCircuitCache();
      const items = await loadCircuit(true);
      setCases(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not write a new circuit");
    } finally {
      setRefreshing(false);
    }
  }

  async function onGenerate(event: FormEvent) {
    event.preventDefault();
    setGenerating(true);
    setError("");
    try {
      const created = await api.generateCase({
        presenting_complaint: complaint || undefined,
        age: age ? Number(age) : undefined,
        gender: gender || undefined,
      });
      router.push(`/station/${created.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="space-y-10">
      <section className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-clinic-dark">Circuit board</p>
          <h1 className="mt-2 max-w-xl font-serif text-5xl leading-[1.05]">
            A new six-station mix every time you reload.
          </h1>
          <p className="mt-4 max-w-2xl text-ink-muted">
            Each visit writes a fresh, diverse circuit across different organ systems. The
            standardized patient still answers only from a hidden case sheet.
          </p>
          <button
            type="button"
            onClick={() => void refreshCircuit()}
            disabled={loading || refreshing}
            className="mt-5 rounded-full border border-black/15 px-4 py-2 text-sm font-medium text-ink hover:border-clinic hover:text-clinic-dark disabled:opacity-50"
          >
            {refreshing ? "Dealing a new circuit…" : "Deal a new circuit"}
          </button>
        </div>
        <form
          onSubmit={onGenerate}
          autoComplete="off"
          className="rounded-2xl border border-black/10 bg-paper-card p-5 shadow-station"
        >
          <h2 className="font-serif text-2xl">Request a custom stem</h2>
          <p className="mt-1 text-sm text-ink-muted">
            LLM mode: <span className="font-medium text-clinic-dark">{llmMode}</span>
          </p>
          <label className="mt-4 block text-sm">
            Presenting complaint
            <input
              value={complaint}
              onChange={(event) => setComplaint(event.target.value)}
              placeholder="e.g. jaundice, hematuria, postpartum headache"
              className="mt-1 w-full rounded-lg border border-black/10 bg-white px-3 py-2 outline-none ring-clinic/30 focus:ring"
            />
          </label>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <label className="text-sm">
              Age
              <input
                type="number"
                min={16}
                max={95}
                value={age}
                onChange={(event) => setAge(event.target.value)}
                placeholder="Any"
                className="mt-1 w-full rounded-lg border border-black/10 bg-white px-3 py-2 outline-none ring-clinic/30 focus:ring"
              />
            </label>
            <label className="text-sm">
              Gender
              <select
                value={gender}
                onChange={(event) => setGender(event.target.value)}
                className="mt-1 w-full rounded-lg border border-black/10 bg-white px-3 py-2 outline-none ring-clinic/30 focus:ring"
              >
                <option value="">Any</option>
                <option value="Female">Female</option>
                <option value="Male">Male</option>
              </select>
            </label>
          </div>
          <button
            type="submit"
            disabled={generating}
            className="mt-5 w-full rounded-full bg-ink px-4 py-2.5 text-sm font-medium text-paper disabled:opacity-60"
          >
            {generating ? "Writing stem…" : "Generate and open station"}
          </button>
        </form>
      </section>

      <p className="rounded-xl border border-clinic/25 bg-clinic-soft/60 px-4 py-3 text-sm text-clinic-dark">
        If it isn’t loading, give it about 60 seconds. The clinic server may be waking up.
      </p>

      {error && (
        <p className="rounded-xl border border-rust/30 bg-rust/10 px-4 py-3 text-sm text-rust">
          {error}
        </p>
      )}

      {loading || refreshing ? (
        <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={index}
              className="h-64 animate-pulse rounded-2xl border border-black/5 bg-paper-card/70"
            />
          ))}
          <p className="text-sm text-ink-muted md:col-span-2 xl:col-span-3">
            Loading stations… If this sits here, give it about 60 seconds.
          </p>
        </section>
      ) : (
        <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {cases.map((item, index) => (
            <CaseCard key={item.id} item={item} index={index} />
          ))}
        </section>
      )}
    </div>
  );
}
