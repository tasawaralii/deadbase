import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // This lives alongside archive/ and backend/ in the same repo, each with
  // their own lockfile - pin the workspace root so Next doesn't guess wrong.
  turbopack: {
    root: path.join(__dirname),
  },
  // Server-side fetch() calls (most of our API calls, since pages fetch in
  // Server Components) never hit the browser Network tab and the Node
  // inspector's Network panel needs --experimental-network-inspection
  // (unsupported under Bun) - log them to the terminal instead.
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  images: {
    remotePatterns: [
      // TMDB-sourced season/episode/anime images.
      { protocol: "https", hostname: "image.tmdb.org" },
      // Legacy migrated post backdrops, not yet re-hosted (see app/media.py "url" source).
      { protocol: "https", hostname: "deadtoons.sbs" },
      // Self-hosted ("local" source) season/anime posters, see MEDIA_BASE_URL.
      { protocol: "https", hostname: "image.deadbase.host" },
      // Author/comment avatars.
      { protocol: "https", hostname: "secure.gravatar.com" },
      // Remaining legacy "url"-sourced anime poster/backdrop domains found in
      // the migrated data (see app/media.py "url" source, Animes.poster_source).
      { protocol: "https", hostname: "m.media-amazon.com" },
      { protocol: "https", hostname: "movieassetsdigital.sgp1.cdn.digitaloceanspaces.com" },
      { protocol: "https", hostname: "img.rgstatic.com" },
      { protocol: "https", hostname: "imgs.search.brave.com" },
      { protocol: "https", hostname: "i.postimg.cc" },
    ],
  },
};

export default nextConfig;
