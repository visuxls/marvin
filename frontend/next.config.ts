import type { NextConfig } from "next";
import { networkInterfaces } from "node:os";

/**
 * Hostnames Next.js should accept for `/_next/*` in development.
 *
 * Accessing the dev server via a LAN IP (e.g. from a phone) is treated as a
 * cross-origin request relative to the bind hostname (`localhost`). Without
 * these entries, Next.js 16 blocks dev resources and client onClick handlers
 * silently stop working on the device.
 */
function lanDevOrigins(): string[] {
  const fromEnv = process.env.ALLOWED_DEV_ORIGINS?.split(",")
    .map((value) => value.trim())
    .filter(Boolean);
  if (fromEnv && fromEnv.length > 0) {
    return fromEnv;
  }

  const origins = new Set<string>();
  try {
    for (const entries of Object.values(networkInterfaces())) {
      for (const entry of entries ?? []) {
        if (entry.family === "IPv4" && !entry.internal) {
          origins.add(entry.address);
        }
      }
    }
  } catch {
    // networkInterfaces can fail in restricted environments; env override covers that.
  }
  return [...origins];
}

const nextConfig: NextConfig = {
  allowedDevOrigins: lanDevOrigins(),
  devIndicators: false,
};

export default nextConfig;
