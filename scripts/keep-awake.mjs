/**
 * Keep the live Render services awake by pinging them.
 * Do not restart the API — a restart wipes in-memory stations and interviews.
 *
 * Usage (leave the window open):
 *   node scripts/keep-awake.mjs
 */
const API = process.env.API_URL ?? "https://osce-simulator-api.onrender.com/api/health";
const WEB = process.env.WEB_URL ?? "https://osce-simulator-web.onrender.com/api/health";
const INTERVAL_MS = Number(process.env.KEEP_AWAKE_MS ?? 60_000);

async function ping(name, url) {
  const started = Date.now();
  try {
    const response = await fetch(url, {
      cache: "no-store",
      signal: AbortSignal.timeout(45_000),
    });
    const body = (await response.text()).slice(0, 80);
    console.log(
      `${new Date().toISOString()}  ${name.padEnd(3)}  ${response.status}  ${Date.now() - started}ms  ${body}`,
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.log(`${new Date().toISOString()}  ${name.padEnd(3)}  FAIL  ${message}`);
  }
}

async function tick() {
  await ping("api", API);
  await ping("web", WEB);
}

console.log(`Pinging every ${INTERVAL_MS / 1000}s. Leave this window open. Ctrl+C to stop.`);
await tick();
setInterval(() => {
  void tick();
}, INTERVAL_MS);
