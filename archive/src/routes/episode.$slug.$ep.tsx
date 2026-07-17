import { createFileRoute, notFound } from "@tanstack/react-router";
import { useEffect, useRef } from "react";
import { Layout } from "@/components/Layout";
import { EpisodeHero } from "@/components/EpisodeHero";
import { EpisodeGallery } from "@/components/EpisodeGallery";
import { DownloadCard } from "@/components/DownloadCard";
import { buildEpisodeViewModel } from "@/data/episode";
import { useAnime, useEpisode, useTrackView } from "@/hooks/use-api";

function parseEp(ep: string): { season: number; episode: number } | null {
  const match = /^(\d+)x(\d+)$/.exec(ep);
  if (!match) return null;
  return { season: Number(match[1]), episode: Number(match[2]) };
}

export const Route = createFileRoute("/episode/$slug/$ep")({
  loader: ({ params }) => {
    if (!parseEp(params.ep)) throw notFound();
  },
  head: ({ params }) => ({
    meta: [{ title: `${params.slug} · ${params.ep} | Deadtoons` }],
  }),
  component: EpisodePage,
  notFoundComponent: () => (
    <Layout>
      <div className="panel p-8 text-center">
        <h1 className="font-display text-2xl">Episode not found</h1>
      </div>
    </Layout>
  ),
});

function EpisodePage() {
  const { slug, ep } = Route.useParams();
  const parsed = parseEp(ep)!;

  const animeQuery = useAnime(slug);
  const episodeQuery = useEpisode(slug, parsed.season, parsed.episode);
  const trackView = useTrackView(episodeQuery.data?.content_id ?? null);

  const tracked = useRef<number | null>(null);
  useEffect(() => {
    const contentId = episodeQuery.data?.content_id;
    if (contentId && tracked.current !== contentId) {
      tracked.current = contentId;
      trackView.mutate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [episodeQuery.data?.content_id]);

  if (animeQuery.isLoading || episodeQuery.isLoading) {
    return (
      <Layout>
        <p className="label-cap text-muted-foreground">Loading…</p>
      </Layout>
    );
  }

  if (animeQuery.isError || episodeQuery.isError || !animeQuery.data || !episodeQuery.data) {
    return (
      <Layout>
        <div className="panel p-8 text-center">
          <h1 className="font-display text-2xl">Couldn't load this episode</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            It may not exist, or have no live download links yet.
          </p>
        </div>
      </Layout>
    );
  }

  const episode = buildEpisodeViewModel(animeQuery.data, parsed.season, episodeQuery.data);

  return (
    <Layout>
      <div className="space-y-5">
        <EpisodeHero episode={episode} />

        <EpisodeGallery images={episode.images} title="Stills" />

        <div id="downloads">
          <div className="mb-3 flex items-baseline gap-3 px-1">
            <h2 className="font-display text-2xl sm:text-3xl">Downloads</h2>
            <span className="label-cap text-muted-foreground">
              {episode.qualities.length} mirrors
            </span>
          </div>
          {episode.qualities.length === 0 ? (
            <p className="panel p-4 text-sm text-muted-foreground">
              No download links available for this episode yet.
            </p>
          ) : (
            <div className="space-y-3">
              {episode.qualities.map((q) => (
                <DownloadCard key={q.id} item={q} />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
