// Mirrors backend/app/schemas/*.py response shapes. Keep in sync by hand -
// there's no shared codegen between the two yet.

export type ImageUrls = {
  low: string;
  mid: string;
  high: string;
};

export type DownloadLink = {
  name: string;
  link_server_id: number;
  color: string;
};

export type LinkPublic = {
  quality: string;
  size: string;
  servers: DownloadLink[];
  only_hindi: boolean;
  note: string;
};

export type AnimeDetail = {
  slug: string;
  anime_name: string;
  type: string;
  poster: ImageUrls;
  backdrop: ImageUrls;
  overview: string;
  duration: number;
  rating: string;
  age_rating: string;
  genres: string[];
  release_date: string | null;
  seasons?: unknown[] | null;
  links?: LinkPublic[] | null;
  watch_servers?: DownloadLink[] | null;
};

export type EpisodeDetail = {
  content_id: number;
  episode_number: number;
  episode_name: string | null;
  overview: string | null;
  img: ImageUrls;
  air_date: string | null;
  episode_runtime: number | null;
  episode_rating: string | null;
  links: LinkPublic[];
  watch_servers: DownloadLink[];
};

export type TrendingEpisodeItem = {
  anime_slug: string;
  anime_name: string;
  season_number: number;
  episode: {
    episode_number: number;
    episode_name: string | null;
    img: ImageUrls;
    air_date: string | null;
    episode_rating: string | null;
    link_count: number;
  };
  views: number;
};

export type TrendingEpisodeList = {
  data: TrendingEpisodeItem[];
};

export type ShortenerOption = {
  id: number;
  name: string;
  message: string | null;
  how_to_video_url: string | null;
  already_solved: boolean;
  reported: boolean;
};

export type UnlockStatus = {
  unlocked: boolean;
  url?: string | null;
  solved?: number | null;
  required?: number | null;
  shorteners?: ShortenerOption[] | null;
};

export type StartUnlockResponse = {
  redirect_url: string;
};

export type Message = {
  message: string;
};
