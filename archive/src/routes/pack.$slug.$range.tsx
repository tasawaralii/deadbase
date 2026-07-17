import { createFileRoute, notFound } from "@tanstack/react-router";
import { Layout } from "@/components/Layout";
import { EpisodeHero } from "@/components/EpisodeHero";
import { DownloadCard } from "@/components/DownloadCard";
import { buildPackViewModel } from "@/data/episode";
import { useAnime, usePack } from "@/hooks/use-api";

function parseRange(range: string): { season: number; start: number; end: number } | null {
  const match = /^(\d+)x(\d+)-(\d+)$/.exec(range);
  if (!match) return null;
  return { season: Number(match[1]), start: Number(match[2]), end: Number(match[3]) };
}

export const Route = createFileRoute("/pack/$slug/$range")({
  loader: ({ params }) => {
    if (!parseRange(params.range)) throw notFound();
  },
  head: ({ params }) => ({
    meta: [{ title: `${params.slug} · ${params.range} | Deadtoons` }],
  }),
  component: PackPage,
  notFoundComponent: () => (
    <Layout>
      <div className="panel p-8 text-center">
        <h1 className="font-display text-2xl">Pack not found</h1>
      </div>
    </Layout>
  ),
});

function PackPage() {
  const { slug, range } = Route.useParams();
  const parsed = parseRange(range)!;

  const animeQuery = useAnime(slug);
  const packQuery = usePack(slug, parsed.season, parsed.start, parsed.end);

  if (animeQuery.isLoading || packQuery.isLoading) {
    return (
      <Layout>
        <p className="label-cap text-muted-foreground">Loading…</p>
      </Layout>
    );
  }

  if (animeQuery.isError || packQuery.isError || !animeQuery.data || !packQuery.data) {
    return (
      <Layout>
        <div className="panel p-8 text-center">
          <h1 className="font-display text-2xl">Couldn't load this pack</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            It may not exist, or have no live download links yet.
          </p>
        </div>
      </Layout>
    );
  }

  const pack = buildPackViewModel(animeQuery.data, parsed.season, packQuery.data);

  return (
    <Layout>
      <div className="space-y-5">
        <EpisodeHero episode={pack} />

        <div id="downloads">
          <div className="mb-3 flex items-baseline gap-3 px-1">
            <h2 className="font-display text-2xl sm:text-3xl">Downloads</h2>
            <span className="label-cap text-muted-foreground">{pack.qualities.length} mirrors</span>
          </div>
          {pack.qualities.length === 0 ? (
            <p className="panel p-4 text-sm text-muted-foreground">
              No download links available for this pack yet.
            </p>
          ) : (
            <div className="space-y-3">
              {pack.qualities.map((q) => (
                <DownloadCard key={q.id} item={q} />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
