import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // used by the Docker image, Vercel ignores it
  output: "standalone",
};

export default nextConfig;
