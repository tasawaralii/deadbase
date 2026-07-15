import { createFileRoute, Link } from "@tanstack/react-router";
import { Flame, Star } from "lucide-react";
import { Layout } from "@/components/Layout";
import { trendingEpisodes } from "@/data/episode";

export const Route = createFileRoute("/trending")({
  head: () => ({
    meta: [
      { title: "Trending Episodes — Deadtoons" },
      { name: "description", content: "The 7 most trending anime episodes from the last 7 days." },
      { property: "og:title", content: "Trending Episodes — Deadtoons" },
      { property: "og:description", content: "The 7 most trending anime episodes from the last 7 days." },
    ],
  }),
  component: TrendingPage,
});

function TrendingPage() {
  return (
    <Layout>
      <section className="space-y-5">
        {/* Header slab */}
        <div className="panel flex items-stretch overflow-hidden">
          <div className="flex items-center justify-center border-r-2 border-border bg-primary px-4 text-primary-foreground sm:px-6">
            <Flame className="h-6 w-6 sm:h-8 sm:w-8" />
          </div>
          <div className="flex-1 p-4 sm:p-6">
            <p className="label-cap text-muted-foreground">Last 7 days · Top 7 Episodes</p>
            <h1 className="mt-1 font-display text-3xl sm:text-5xl">Trending This Week</h1>
          </div>
          <div className="hidden items-center border-l-2 border-border bg-accent px-6 text-accent-foreground sm:flex">
            <span className="font-display text-5xl leading-none">07</span>
          </div>
        </div>

        {/* Grid — 2 cols on mobile, dense */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
          {trendingEpisodes.map((ep, i) => (
            <Link
              key={`${ep.animeSlug}-${ep.episodeNumber}`}
              to="/episode/$slug/$ep"
              params={{ slug: ep.animeSlug, ep: `${ep.seasonNumber}x${ep.episodeNumber}` }}
              className="panel group relative overflow-hidden transition hover:-translate-x-0.5 hover:-translate-y-0.5"
            >
              {/* 16:9 still */}
              <div className="relative aspect-video w-full overflow-hidden border-b-2 border-border bg-ink">
                <img
                  src={ep.poster}
                  alt={ep.animeTitle}
                  loading="lazy"
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                {/* Rank chip — corner tag instead of oversize numeral */}
                <span className="absolute left-0 top-0 flex items-center gap-1 border-b-2 border-r-2 border-border bg-primary px-2 py-1 font-mono text-[10px] font-black uppercase tracking-widest text-primary-foreground">
                  #{(i + 1).toString().padStart(2, "0")}
                </span>
                {/* Rating chip */}
                <span className="absolute right-2 top-2 flex items-center gap-1 border-2 border-border bg-accent px-1.5 py-0.5 font-mono text-[10px] font-bold text-accent-foreground">
                  <Star className="h-2.5 w-2.5 fill-current" />
                  {ep.rating.toFixed(1)}
                </span>
              </div>

              {/* Meta */}
              <div className="flex items-start justify-between gap-2 p-3">
                <div className="min-w-0">
                  <p className="label-cap truncate text-primary">{ep.animeTitle}</p>
                  <h3 className="mt-1 line-clamp-1 font-display text-base leading-tight sm:text-lg">
                    {ep.title}
                  </h3>
                </div>
                <span className="shrink-0 border-2 border-border bg-secondary px-1.5 py-0.5 font-mono text-[10px] font-black uppercase tracking-wider text-secondary-foreground">
                  EP {ep.episodeNumber.toString().padStart(2, "0")}
                </span>
              </div>
            </Link>
          ))}
        </div>

      </section>
    </Layout>
  );
}
