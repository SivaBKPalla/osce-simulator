import type { NextConfig } from "next";

const rawTarget = process.env.API_PROXY_TARGET ?? "http://127.0.0.1:8000";
const apiTarget = rawTarget.startsWith("http") ? rawTarget : `https://${rawTarget}`;

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiTarget}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
