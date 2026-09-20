import type {
  EvaluationResult,
  GenerateCasePayload,
  SessionResponse,
  VisibleCase,
  ChatMessage,
} from "./types";

const PRODUCTION_API = "https://osce-simulator-api.onrender.com";
const ATTEMPTS = 3;
const ATTEMPT_MS = 12_000;

function apiBase() {
  const fromEnv = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");
  if (fromEnv) return fromEnv;
  if (typeof window !== "undefined" && /\.onrender\.com$/i.test(window.location.hostname)) {
    return PRODUCTION_API;
  }
  return "";
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isTransientStatus(status: number) {
  return status === 502 || status === 503 || status === 504;
}

function timeoutSignal(ms: number) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  return { controller, timer };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let lastError: Error = new Error("Could not reach the clinic API.");

  for (let attempt = 0; attempt < ATTEMPTS; attempt += 1) {
    const { controller, timer } = timeoutSignal(ATTEMPT_MS);
    try {
      const response = await fetch(`${apiBase()}${path}`, {
        ...init,
        headers: {
          "Content-Type": "application/json",
          ...(init?.headers ?? {}),
        },
        cache: "no-store",
        signal: controller.signal,
      });

      if (isTransientStatus(response.status) && attempt < ATTEMPTS - 1) {
        await sleep(1_500);
        continue;
      }

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Request failed: ${response.status}`);
      }

      return (await response.json()) as T;
    } catch (error) {
      lastError = error instanceof Error ? error : lastError;
      if (attempt >= ATTEMPTS - 1) break;
      await sleep(1_500);
    } finally {
      clearTimeout(timer);
    }
  }

  throw lastError;
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
