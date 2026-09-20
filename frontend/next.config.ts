import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // /api is proxied at runtime by app/api/[...path] so production never
  // bakes in http://127.0.0.1:8000 the way next.config rewrites would.
};

export default nextConfig;
