import { apiOrigin } from "@/lib/api-origin";

function pingApi() {
  void fetch(`${apiOrigin()}/api/health`, {
    cache: "no-store",
    signal: AbortSignal.timeout(12_000),
  }).catch(() => undefined);
}

export async function register() {
  if (process.env.NEXT_RUNTIME !== "nodejs") {
    return;
  }
  pingApi();
  setInterval(pingApi, 8 * 60 * 1000);
}
