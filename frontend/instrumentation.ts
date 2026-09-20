import { apiOrigin } from "@/lib/api-origin";

async function pingApi() {
  try {
    await fetch(`${apiOrigin()}/api/health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(45_000),
    });
  } catch {
    // The next user request still retries if this ping misses.
  }
}

export async function register() {
  if (process.env.NEXT_RUNTIME !== "nodejs") {
    return;
  }
  await pingApi();
  setInterval(() => {
    void pingApi();
  }, 8 * 60 * 1000);
}
