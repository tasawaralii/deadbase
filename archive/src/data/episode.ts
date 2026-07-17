import type { AnimeDetail, EpisodeDetail } from "@/lib/types";

export type DownloadLink = {
  name: string;
  link_server_id: number;
  color: string;
};

export type DownloadQuality = {
  id: string;
  quality: string;
  size: string;
  links: DownloadLink[];
};

export type Episode = {
  animeSlug: string;
  animeTitle: string;
  contentId: number;
  seasonNumber: number;
  episodeNumber: number;
  title: string;
  description: string;
  poster: string;
  images: string[];
  rating: number;
  releaseDate: string;
  duration: string;
  qualities: DownloadQuality[];
};

function formatDuration(minutes: number | null | undefined): string {
  if (!minutes) return "—";
  return `${minutes} min`;
}

function bestImage(img: { low: string; mid: string; high: string } | undefined): string {
  if (!img) return "";
  return img.high || img.mid || img.low;
}

export function buildEpisodeViewModel(
  anime: AnimeDetail,
  seasonNumber: number,
  ep: EpisodeDetail,
): Episode {
  return {
    animeSlug: anime.slug,
    animeTitle: anime.anime_name,
    contentId: ep.content_id,
    seasonNumber,
    episodeNumber: ep.episode_number,
    title: ep.episode_name ?? `Episode ${ep.episode_number}`,
    description: ep.overview || anime.overview,
    poster: bestImage(anime.poster),
    images: ep.img ? [bestImage(ep.img)].filter(Boolean) : [],
    rating: Number(ep.episode_rating ?? anime.rating ?? 0),
    releaseDate: ep.air_date ?? anime.release_date ?? "",
    duration: formatDuration(ep.episode_runtime ?? anime.duration),
    qualities: ep.links.map((link, i) => ({
      id: `${link.quality}-${i}`,
      quality: link.quality,
      size: link.size,
      links: link.servers.map((s) => ({
        name: s.name,
        link_server_id: s.link_server_id,
        color: s.color,
      })),
    })),
  };
}
