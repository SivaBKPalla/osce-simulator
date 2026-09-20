import type {
  EvaluationResult,
  GenerateCasePayload,
  SessionResponse,
  VisibleCase,
  ChatMessage,
} from "./types";

const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");

const UNREACHABLE =
  "The clinic API is waking up or unreachable. Free hosting sleeps when idle — wait a few seconds and reload.";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

async function withWake<T>(fn: () => Promise<T>, attempts = 6): Promise<T> {
  let last: unknown;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      return await fn();
    } catch (err) {
      last = err;
      await new Promise((resolve) => setTimeout(resolve, 2500 * (attempt + 1)));
    }
  }
  throw last instanceof Error ? last : new Error(UNREACHABLE);
}

export const api = {
  health: () => request<{ status: string; llm: string }>("/api/health"),
  listCases: () => request<VisibleCase[]>("/api/cases"),
  freshCircuit: (force = false) =>
    request<VisibleCase[]>(`/api/cases/circuit${force ? "?force=true" : ""}`, {
      method: "POST",
    }),
  getCase: (id: string) => request<VisibleCase>(`/api/cases/${id}`),
  generateCase: (payload: GenerateCasePayload) =>
    request<VisibleCase>("/api/cases/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  startSession: (caseId: string) =>
    request<SessionResponse>("/api/sessions", {
      method: "POST",
      body: JSON.stringify({ case_id: caseId }),
    }),
  getSession: (sessionId: string) => request<SessionResponse>(`/api/sessions/${sessionId}`),
  sendChat: (sessionId: string, message: string) =>
    request<ChatMessage>(`/api/sessions/${sessionId}/chat`, {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  wake: () => withWake(() => request<{ status: string; llm: string }>("/api/health")),
  withWake,
  evaluate: (
    sessionId: string,
    payload: {
      differential_1: string;
      differential_2: string;
      differential_3: string;
      next_steps: string;
    },
  ) =>
    request<EvaluationResult>(`/api/sessions/${sessionId}/evaluate`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
