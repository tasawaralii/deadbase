import type { AnimeDetail, EpisodeDetail, LinkPublic, PackDetail } from "@/lib/types";

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

// Shared view-model for anything with a download-links page: episodes,
// movies, and packs all render through EpisodeHero + DownloadCard.
// seasonNumber/episodeNumber are only set for episodes (packs get a season
// but no single episode number; movies get neither) - EpisodeHero hides
// those badges when they're absent. contentId is only set for movies/
// episodes - packs aren't individually trackable, so it's left out and no
// view gets recorded for them.
export type Episode = {
  animeSlug: string;
  animeTitle: string;
  contentId?: number;
  seasonNumber?: number;
  episodeNumber?: number;
  title: string;
  description: string;
  poster: string;
  images: string[];
  rating: number;
  releaseDate: string;
  duration: string;
  qualities: DownloadQuality[];
  // Streaming isn't built yet - always false until a real source exists.
  // EpisodeHero hides the "Watch Online" action when this is false.
  hasWatchServers: boolean;
};

function formatDuration(minutes: number | null | undefined): string {
  if (!minutes) return "—";
  return `${minutes} min`;
}

function bestImage(img: { low: string; mid: string; high: string } | undefined): string {
  if (!img) return "";
  return img.high || img.mid || img.low;
}

function mapLinksToQualities(links: LinkPublic[]): DownloadQuality[] {
  return links.map((link, i) => ({
    id: `${link.quality}-${i}`,
    quality: link.quality,
    size: link.size,
    links: link.servers.map((s) => ({
      name: s.name,
      link_server_id: s.link_server_id,
      color: s.color,
    })),
  }));
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
    qualities: mapLinksToQualities(ep.links),
    hasWatchServers: ep.watch_servers.length > 0,
  };
}

export function buildPackViewModel(
  anime: AnimeDetail,
  seasonNumber: number,
  pack: PackDetail,
): Episode {
  return {
    animeSlug: anime.slug,
    animeTitle: anime.anime_name,
    seasonNumber,
    title: pack.pack_name || `Episodes ${pack.start_ep}-${pack.end_ep}`,
    description: anime.overview,
    poster: bestImage(anime.poster),
    images: [],
    rating: Number(anime.rating ?? 0),
    releaseDate: anime.release_date ?? "",
    duration: formatDuration(anime.duration),
    qualities: mapLinksToQualities(pack.links),
    hasWatchServers: false,
  };
}

export function buildMovieViewModel(anime: AnimeDetail): Episode {
  return {
    animeSlug: anime.slug,
    animeTitle: anime.anime_name,
    contentId: anime.content_id,
    title: anime.anime_name,
    description: anime.overview,
    poster: bestImage(anime.poster),
    images: anime.backdrop ? [bestImage(anime.backdrop)].filter(Boolean) : [],
    rating: Number(anime.rating ?? 0),
    releaseDate: anime.release_date ?? "",
    duration: formatDuration(anime.duration),
    qualities: mapLinksToQualities(anime.links ?? []),
    hasWatchServers: (anime.watch_servers ?? []).length > 0,
  };
}
