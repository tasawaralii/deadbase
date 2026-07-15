import { createFileRoute } from "@tanstack/react-router";
import { Layout } from "@/components/Layout";
import { EpisodeHero } from "@/components/EpisodeHero";
import { EpisodeGallery } from "@/components/EpisodeGallery";
import { DownloadCard } from "@/components/DownloadCard";
import { episode } from "@/data/episode";

export const Route = createFileRoute("/episode/$slug/$ep")({
  head: () => ({
    meta: [
      { title: `Episode ${episode.episodeNumber} — ${episode.animeTitle} | Deadtoons` },
      { name: "description", content: episode.description },
      { property: "og:title", content: `${episode.animeTitle} · Episode ${episode.episodeNumber}` },
      { property: "og:description", content: episode.description },
    ],
  }),
  component: EpisodePage,
});

function EpisodePage() {
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
          <div className="space-y-3">
            {episode.qualities.map((q) => (
              <DownloadCard key={q.id} item={q} />
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
