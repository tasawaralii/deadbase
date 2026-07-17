import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef } from "react";
import { Layout } from "@/components/Layout";
import { EpisodeHero } from "@/components/EpisodeHero";
import { EpisodeGallery } from "@/components/EpisodeGallery";
import { DownloadCard } from "@/components/DownloadCard";
import { buildMovieViewModel } from "@/data/episode";
import { useAnime, useTrackView } from "@/hooks/use-api";

export const Route = createFileRoute("/movie/$slug")({
  head: ({ params }) => ({
    meta: [{ title: `${params.slug} | Deadtoons` }],
  }),
  component: MoviePage,
});

function MoviePage() {
  const { slug } = Route.useParams();
  const animeQuery = useAnime(slug);
  const trackView = useTrackView(animeQuery.data?.content_id ?? null);

  const tracked = useRef<number | null>(null);
  useEffect(() => {
    const contentId = animeQuery.data?.content_id;
    if (animeQuery.data?.type === "movie" && contentId && tracked.current !== contentId) {
      tracked.current = contentId;
      trackView.mutate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [animeQuery.data?.content_id, animeQuery.data?.type]);

  if (animeQuery.isLoading) {
    return (
      <Layout>
        <p className="label-cap text-muted-foreground">Loading…</p>
      </Layout>
    );
  }

  if (animeQuery.isError || !animeQuery.data || animeQuery.data.type !== "movie") {
    return (
      <Layout>
        <div className="panel p-8 text-center">
          <h1 className="font-display text-2xl">Couldn't load this movie</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            It may not exist, or have no live download links yet.
          </p>
        </div>
      </Layout>
    );
  }

  const movie = buildMovieViewModel(animeQuery.data);

  return (
    <Layout>
      <div className="space-y-5">
        <EpisodeHero episode={movie} />

        <EpisodeGallery images={movie.images} title="Backdrop" />

        <div id="downloads">
          <div className="mb-3 flex items-baseline gap-3 px-1">
            <h2 className="font-display text-2xl sm:text-3xl">Downloads</h2>
            <span className="label-cap text-muted-foreground">
              {movie.qualities.length} mirrors
            </span>
          </div>
          {movie.qualities.length === 0 ? (
            <p className="panel p-4 text-sm text-muted-foreground">
              No download links available for this movie yet.
            </p>
          ) : (
            <div className="space-y-3">
              {movie.qualities.map((q) => (
                <DownloadCard key={q.id} item={q} />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
