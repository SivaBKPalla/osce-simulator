import { apiOrigin, isTransientStatus, sleep } from "@/lib/api-origin";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const ATTEMPTS = 6;

async function proxy(request: Request, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const incoming = new URL(request.url);
  const target = `${apiOrigin()}/api/${path.join("/")}${incoming.search}`;
  const method = request.method.toUpperCase();
  const body =
    method === "GET" || method === "HEAD" ? undefined : await request.arrayBuffer();
  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("content-type", contentType);
  }

  for (let attempt = 0; attempt < ATTEMPTS; attempt += 1) {
    try {
      const response = await fetch(target, {
        method,
        headers,
        body,
        cache: "no-store",
        redirect: "manual",
        signal: AbortSignal.timeout(60_000),
      });
      if (isTransientStatus(response.status) && attempt < ATTEMPTS - 1) {
        await sleep(3_000 + attempt * 2_000);
        continue;
      }
      const payload = await response.arrayBuffer();
      const outbound = new Headers();
      const responseType = response.headers.get("content-type");
      if (responseType) {
        outbound.set("content-type", responseType);
      }
      return new Response(payload, { status: response.status, headers: outbound });
    } catch {
      if (attempt < ATTEMPTS - 1) {
        await sleep(3_000 + attempt * 2_000);
      }
    }
  }

  return Response.json(
    { detail: "The clinic API is starting. Reload in a moment if this persists." },
    { status: 503 },
  );
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
