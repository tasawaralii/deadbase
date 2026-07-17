import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // This lives alongside archive/ and backend/ in the same repo, each with
  // their own lockfile - pin the workspace root so Next doesn't guess wrong.
  turbopack: {
    root: path.join(__dirname),
  },
};

export default nextConfig;
