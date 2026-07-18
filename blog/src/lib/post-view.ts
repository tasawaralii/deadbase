import type { PostDetail } from "@/lib/types";

const ARCHIVE_URL = process.env.NEXT_PUBLIC_ARCHIVE_URL ?? "http://localhost:5173";

export type LanguageMode = "Single" | "Dual" | "Multi";

export type EpisodeRow = {
  episodeNumber: number;
  name: string;
  note: string | null;
  href: string;
};

export type PackRow = {
  label: string;
  href: string;
};

export type PostView = {
  isMovie: boolean;
  overview: string;
  posterUrl: string;
  backdropUrl: string;
  releaseDate: string | null;
  releaseYear: string | null;
  genres: string[];
  rating: string | null;
  ageRating: string | null;
  durationMinutes: number | null;
  languageMode: LanguageMode | null;
  languages: string[];
  otts: string[];
  totalEpisodes: number | null;
  episodes: EpisodeRow[];
  skippedEpisodes: number[];
  packs: PackRow[];
  movieHref: string | null;
  screenshots: string[];
};

function stripEpisodePrefix(name: string): string {
  return name.replace(/^Episode \d+:\s*/, "");
}

export function buildPostView(post: PostDetail): PostView {
  const isMovie = post.anime !== null;
  const season = post.season;
  const anime = post.anime;

  const dubs = season?.dubs ?? [];
  const languages = [...new Set(dubs.map((d) => d.language))];
  const otts = [...new Set(dubs.map((d) => d.platform))];
  const languageMode: LanguageMode | null =
    languages.length === 0
      ? null
      : languages.length === 1
        ? "Single"
        : languages.length === 2
          ? "Dual"
          : "Multi";

  const episodes = season?.episodes ?? [];
  const episodeRows: EpisodeRow[] = episodes.map((e) => ({
    episodeNumber: e.episode_number,
    name: stripEpisodePrefix(e.episode_name ?? `Episode ${e.episode_number}`),
    note: e.note,
    href: `${ARCHIVE_URL}/episode/${post.anime_slug}/${season?.season_number}x${e.episode_number}`,
  }));

  const skippedEpisodes: number[] = [];
  for (let i = 1; i < episodes.length; i++) {
    const prev = episodes[i - 1].episode_number;
    const cur = episodes[i].episode_number;
    for (let n = prev + 1; n < cur; n++) skippedEpisodes.push(n);
  }

  const packRows: PackRow[] = (season?.packs ?? []).map((p) => ({
    label: `Episodes ${p.start_ep} – ${p.end_ep}`,
    href: `${ARCHIVE_URL}/pack/${post.anime_slug}/${season?.season_number}x${p.start_ep}-${p.end_ep}`,
  }));

  const screenshots = episodes
    .map((e) => e.img.high || e.img.mid)
    .filter((src): src is string => Boolean(src))
    .slice(0, 8);

  const releaseDate = season?.release_date ?? anime?.release_date ?? null;

  // TMDB-sourced ratings/duration are often "0" or "0.00" when not yet
  // populated - treat those as absent rather than rendering "0.00 / 10".
  const ratingValue = season?.rating ?? anime?.rating ?? null;
  const rating = ratingValue && parseFloat(ratingValue) > 0 ? ratingValue : null;
  const ageRating = anime?.age_rating || null;
  const durationMinutes = anime?.duration && anime.duration > 0 ? anime.duration : null;

  return {
    isMovie,
    overview: season?.overview ?? anime?.overview ?? "",
    posterUrl: season?.poster.mid || anime?.poster.mid || "",
    backdropUrl: post.backdrop_img.high || post.backdrop_img.mid || post.backdrop_img.low,
    releaseDate,
    releaseYear: releaseDate ? releaseDate.slice(0, 4) : null,
    genres: post.genres,
    rating,
    ageRating,
    durationMinutes,
    languageMode,
    languages,
    otts,
    totalEpisodes: season?.total_episodes ?? null,
    episodes: episodeRows,
    skippedEpisodes,
    packs: packRows,
    movieHref: isMovie ? `${ARCHIVE_URL}/movie/${post.anime_slug}` : null,
    screenshots,
  };
}
