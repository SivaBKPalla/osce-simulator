import { isTransientStatus, sleep } from "./api-origin";
import type {
  EvaluationResult,
  GenerateCasePayload,
  SessionResponse,
  VisibleCase,
  ChatMessage,
} from "./types";

const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");
const ATTEMPTS = 6;

const UNREACHABLE =
  "The clinic API is starting. Stay on this page — it will keep trying, then reload if it is still down.";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let lastError: Error = new Error(UNREACHABLE);

  for (let attempt = 0; attempt < ATTEMPTS; attempt += 1) {
    try {
      const response = await fetch(`${API_BASE}${path}`, {
        ...init,
        headers: {
          "Content-Type": "application/json",
          ...(init?.headers ?? {}),
        },
        cache: "no-store",
        signal: AbortSignal.timeout(60_000),
      });

      if (isTransientStatus(response.status) && attempt < ATTEMPTS - 1) {
        await sleep(3_000 + attempt * 2_000);
        continue;
      }

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Request failed: ${response.status}`);
      }

      return (await response.json()) as T;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(UNREACHABLE);
      const canRetry =
        attempt < ATTEMPTS - 1 &&
        (lastError.name === "TimeoutError" ||
          lastError.name === "AbortError" ||
          lastError.message.includes("Failed to fetch") ||
          lastError.message.includes("NetworkError") ||
          lastError.message.includes("503") ||
          lastError.message.includes("502") ||
          lastError.message.includes("504"));
      if (!canRetry) {
        throw lastError;
      }
      await sleep(3_000 + attempt * 2_000);
    }
  }

  throw lastError;
}

export const api = {
  health: () => request<{ status: string; llm: string }>("/api/health"),
  wake: () => request<{ status: string; llm: string }>("/api/health"),
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
