"use client";

import { FormEvent, Suspense, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { VitalsStrip } from "@/components/VitalsStrip";
import { api } from "@/lib/api";
import type { ChatMessage, VisibleCase } from "@/lib/types";

const SUGGESTIONS = [
  "When did this start, and what were you doing?",
  "Can you describe the pain?",
  "Does anything make it better or worse?",
  "Have you had this before?",
  "What medications do you take?",
];

export default function InterviewPage() {
  return (
    <Suspense fallback={<p className="text-ink-muted">Entering the room…</p>}>
      <InterviewClient />
    </Suspense>
  );
}

function InterviewClient() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session");
  const [item, setItem] = useState<VisibleCase | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [elapsed, setElapsed] = useState(0);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sessionId) {
      setError("Missing session. Return to the station brief.");
      return;
    }
    api
      .getSession(sessionId)
      .then((data) => {
        setItem(data.case);
        setMessages(data.session.messages);
      })
      .catch(() => setError("Session expired. Start the station again."));
  }, [sessionId]);

  useEffect(() => {
    const timer = window.setInterval(() => setElapsed((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  const clock = useMemo(() => {
    const minutes = String(Math.floor(elapsed / 60)).padStart(2, "0");
    const seconds = String(elapsed % 60).padStart(2, "0");
    return `${minutes}:${seconds}`;
  }, [elapsed]);

  async function send(text: string) {
    if (!sessionId || !text.trim() || sending) return;
    const content = text.trim();
    setDraft("");
    setSending(true);
    setError("");
    const optimistic: ChatMessage = {
      role: "student",
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((current) => [...current, optimistic]);
    try {
      const reply = await api.sendChat(sessionId, content);
      setMessages((current) => [...current, reply]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The patient did not respond");
    } finally {
      setSending(false);
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    void send(draft);
  }

  if (!item && !error) {
    return <p className="text-ink-muted">Entering the room…</p>;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[0.9fr_1.3fr]">
      <aside className="space-y-4">
        <Link href={`/station/${params.id}`} className="text-sm text-clinic-dark hover:underline">
          ← Station brief
        </Link>
        <section className="rounded-2xl border border-black/10 bg-paper-card p-5 shadow-station">
          <div className="flex items-center justify-between">
            <p className="text-xs uppercase tracking-[0.2em] text-ink-muted">Live station</p>
            <p className="rounded-full bg-ink px-2.5 py-1 font-mono text-xs text-paper">{clock}</p>
          </div>
          <h1 className="mt-3 font-serif text-3xl">{item?.title ?? "Interview"}</h1>
          {item && (
            <>
              <p className="mt-2 text-sm text-ink-muted">
                {item.age}-year-old {item.gender.toLowerCase()} · {item.presenting_complaint}
              </p>
              <div className="mt-4">
                <VitalsStrip vitals={item.vitals} />
              </div>
              <p className="mt-4 text-sm leading-6 text-ink-muted">{item.brief_history}</p>
            </>
          )}
        </section>
      </aside>

      <section className="flex min-h-[70vh] flex-col rounded-2xl border border-black/10 bg-paper-card shadow-station">
        <div className="border-b border-black/10 px-5 py-4">
          <p className="font-medium">Standardized patient</p>
          <p className="text-sm text-ink-muted">Answers only from the hidden case sheet</p>
        </div>
        <div ref={listRef} className="station-rule flex-1 space-y-3 overflow-y-auto px-5 py-5">
          {messages.length === 0 && (
            <p className="text-sm text-ink-muted">
              The patient is seated. Begin with an open question.
            </p>
          )}
          {messages.map((message, index) => (
            <div
              key={`${message.created_at}-${index}`}
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                message.role === "student"
                  ? "ml-auto bg-clinic text-white"
                  : "bg-white ring-1 ring-black/10"
              }`}
            >
              <p className="mb-1 text-[10px] uppercase tracking-[0.16em] opacity-70">
                {message.role === "student" ? "You" : "Patient"}
              </p>
              {message.content}
            </div>
          ))}
          {sending && <p className="text-sm text-ink-muted">Patient is thinking…</p>}
        </div>
        <div className="space-y-3 border-t border-black/10 p-4">
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => void send(prompt)}
                className="rounded-full border border-black/10 px-3 py-1 text-xs text-ink-muted hover:border-clinic hover:text-clinic-dark"
              >
                {prompt}
              </button>
            ))}
          </div>
          {error && <p className="text-sm text-rust">{error}</p>}
          <form onSubmit={onSubmit} className="flex gap-2">
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask a history question…"
              className="flex-1 rounded-full border border-black/10 bg-white px-4 py-2.5 outline-none ring-clinic/30 focus:ring"
            />
            <button
              type="submit"
              disabled={sending || !draft.trim()}
              className="rounded-full bg-ink px-4 py-2.5 text-sm text-paper disabled:opacity-50"
            >
              Ask
            </button>
          </form>
          <button
            type="button"
            disabled={!sessionId}
            onClick={() =>
              router.push(`/station/${params.id}/submit?session=${sessionId ?? ""}`)
            }
            className="w-full rounded-full bg-clinic px-4 py-2.5 text-sm font-medium text-white hover:bg-clinic-dark"
          >
            End interview and submit differentials
          </button>
        </div>
      </section>
    </div>
  );
}
