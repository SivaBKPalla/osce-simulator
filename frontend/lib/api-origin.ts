export const PRODUCTION_API = "https://osce-simulator-api.onrender.com";

export function apiOrigin() {
  const raw =
    process.env.API_PROXY_TARGET ||
    (process.env.RENDER || process.env.NODE_ENV === "production"
      ? PRODUCTION_API
      : "http://127.0.0.1:8000");
  const withProtocol = raw.startsWith("http") ? raw : `https://${raw}`;
  return withProtocol.replace(/\/$/, "");
}

export function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function isTransientStatus(status: number) {
  return status === 502 || status === 503 || status === 504;
}
