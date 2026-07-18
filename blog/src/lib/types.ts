// Mirrors backend/app/schemas/*.py response shapes. Keep in sync by hand -
// there's no shared codegen between the two yet.

export type ImageUrls = {
  low: string;
  mid: string;
  high: string;
};

export type AuthorPublic = {
  display_name: string;
  slug: string;
  avatar_url: string;
};

export type SeasonDub = {
  platform: string;
  language: string;
};

export type EpisodeSummary = {
  episode_number: number;
  episode_name: string | null;
  note: string | null;
  img: ImageUrls;
  air_date: string | null;
  episode_rating: string | null;
  link_count: number;
};

export type PackSummary = {
  pack_name: string;
  start_ep: number;
  end_ep: number;
  link_count: number;
};

export type SeasonDetail = {
  season_number: number;
  season_name: string;
  poster: ImageUrls;
  overview: string;
  rating: string;
  release_date: string | null;
  total_episodes: number;
  dubs: SeasonDub[];
  episodes: EpisodeSummary[];
  packs: PackSummary[];
};

// Blog only needs enough of the movie/anime shape to render "Series Info" and
// link out to the archive site - it never renders download links itself.
export type AnimeDetail = {
  content_id: number;
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
};

export type PostStatus = "ongoing" | "completed";

export type PostSummary = {
  slug: string;
  title: string;
  backdrop_img: ImageUrls;
  status: PostStatus;
  sticky: boolean;
  views: number;
  last_updated: string;
  tags: string[];
  comment_count: number;
  author: AuthorPublic | null;
  anime_slug: string;
  anime_name: string;
  season_number: number | null;
  type: "movie" | "tv";
};

export type PostListPublic = {
  data: PostSummary[];
  page: number;
  limit: number;
  count: number;
};

export type PostDetail = {
  slug: string;
  title: string;
  backdrop_img: ImageUrls;
  status: PostStatus;
  sticky: boolean;
  views: number;
  last_updated: string;
  tags: string[];
  author: AuthorPublic | null;
  anime_slug: string;
  anime_name: string;
  genres: string[];
  anime: AnimeDetail | null;
  season: SeasonDetail | null;
};

export type CommentPublic = {
  id: number;
  parent_id: number | null;
  author_name: string;
  author_url: string | null;
  avatar_url: string;
  body: string;
  created_at: string;
};

export type CommentCreate = {
  author_name: string;
  author_email: string;
  author_url?: string | null;
  body: string;
  parent_id?: number | null;
};

export type CommentListPublic = {
  data: CommentPublic[];
  page: number;
  limit: number;
  root_count: number;
  total_count: number;
};
