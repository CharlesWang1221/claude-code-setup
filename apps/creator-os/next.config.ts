import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 靜態匯出到 ./out，由 Worker 的 ASSETS 只對外提供 /traffic（見 worker/src/index.ts isPublicAsset）。
  output: "export",
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;
