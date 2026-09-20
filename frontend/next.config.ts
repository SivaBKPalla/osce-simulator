import type { NextConfig } from "next";

const rawTarget =
  process.env.API_PROXY_TARGET ??
  (process.env.RENDER || process.env.NODE_ENV === "production"
    ? "https://osce-simulator-api.onrender.com"
    : "http://127.0.0.1:8000");
const apiTarget = (rawTarget.startsWith("http") ? rawTarget : `https://${rawTarget}`).replace(
  /\/$/,
  "",
);

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
