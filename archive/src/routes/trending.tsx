import { createFileRoute, Link } from "@tanstack/react-router";
import { Flame, Star } from "lucide-react";
import { Layout } from "@/components/Layout";
import { useTrendingEpisodes } from "@/hooks/use-api";

export const Route = createFileRoute("/trending")({
  head: () => ({
    meta: [
      { title: "Trending Episodes — Deadtoons" },
      { name: "description", content: "The most trending anime episodes from the last 7 days." },
      { property: "og:title", content: "Trending Episodes — Deadtoons" },
      {
        property: "og:description",
        content: "The most trending anime episodes from the last 7 days.",
      },
    ],
  }),
  component: TrendingPage,
});

function TrendingPage() {
  const { data, isLoading, isError } = useTrendingEpisodes("week", 12);
  const episodes = data?.data ?? [];

  return (
    <Layout>
      <section className="space-y-5">
        {/* Header slab */}
        <div className="panel flex items-stretch overflow-hidden">
          <div className="flex items-center justify-center border-r-2 border-border bg-primary px-4 text-primary-foreground sm:px-6">
            <Flame className="h-6 w-6 sm:h-8 sm:w-8" />
          </div>
          <div className="flex-1 p-4 sm:p-6">
            <p className="label-cap text-muted-foreground">Last 7 days</p>
            <h1 className="mt-1 font-display text-3xl sm:text-5xl">Trending This Week</h1>
          </div>
        </div>

        {isLoading && <p className="label-cap text-muted-foreground">Loading…</p>}

        {isError && (
          <p className="panel p-4 text-sm text-muted-foreground">
            Couldn't load trending episodes right now.
          </p>
        )}

        {!isLoading && !isError && episodes.length === 0 && (
          <p className="panel p-4 text-sm text-muted-foreground">
            Nothing trending yet — check back soon.
          </p>
        )}

        {/* Grid — 2 cols on mobile, dense */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
          {episodes.map((item, i) => {
            const poster = item.episode.img.high || item.episode.img.mid || item.episode.img.low;
            const rating = item.episode.episode_rating ? Number(item.episode.episode_rating) : null;
            return (
              <Link
                key={`${item.anime_slug}-${item.season_number}-${item.episode.episode_number}`}
                to="/episode/$slug/$ep"
                params={{
                  slug: item.anime_slug,
                  ep: `${item.season_number}x${item.episode.episode_number}`,
                }}
                className="panel group relative overflow-hidden transition hover:-translate-x-0.5 hover:-translate-y-0.5"
              >
                {/* 16:9 still */}
                <div className="relative aspect-video w-full overflow-hidden border-b-2 border-border bg-ink">
                  {poster && (
                    <img
                      src={poster}
                      alt={item.anime_name}
                      loading="lazy"
                      className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                  )}
                  <span className="absolute left-0 top-0 flex items-center gap-1 border-b-2 border-r-2 border-border bg-primary px-2 py-1 font-mono text-[10px] font-black uppercase tracking-widest text-primary-foreground">
                    #{(i + 1).toString().padStart(2, "0")}
                  </span>
                  {rating !== null && (
                    <span className="absolute right-2 top-2 flex items-center gap-1 border-2 border-border bg-accent px-1.5 py-0.5 font-mono text-[10px] font-bold text-accent-foreground">
                      <Star className="h-2.5 w-2.5 fill-current" />
                      {rating.toFixed(1)}
                    </span>
                  )}
                </div>

                {/* Meta */}
                <div className="flex items-start justify-between gap-2 p-3">
                  <div className="min-w-0">
                    <p className="label-cap truncate text-primary">{item.anime_name}</p>
                    <h3 className="mt-1 line-clamp-1 font-display text-base leading-tight sm:text-lg">
                      {item.episode.episode_name ?? `Episode ${item.episode.episode_number}`}
                    </h3>
                  </div>
                  <span className="shrink-0 border-2 border-border bg-secondary px-1.5 py-0.5 font-mono text-[10px] font-black uppercase tracking-wider text-secondary-foreground">
                    EP {item.episode.episode_number.toString().padStart(2, "0")}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      </section>
    </Layout>
  );
}
