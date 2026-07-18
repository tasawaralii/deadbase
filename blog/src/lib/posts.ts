import { api } from "@/lib/api";
import type {
  CommentCreate,
  CommentListPublic,
  CommentPublic,
  PostDetail,
  PostListPublic,
} from "@/lib/types";

function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export type PostListParams = {
  q?: string;
  genre?: string;
  tag?: string;
  author?: string;
  type?: "movie" | "tv";
  status?: "ongoing" | "completed";
  page?: number;
  limit?: number;
};

export function getPosts(params: PostListParams = {}) {
  return api.get<PostListPublic>(`/posts${buildQuery(params)}`);
}

export function getPost(slug: string) {
  return api.get<PostDetail>(`/posts/${encodeURIComponent(slug)}`);
}

export type CommentListParams = {
  page?: number;
  limit?: number;
};

export function getComments(slug: string, params: CommentListParams = {}) {
  return api.get<CommentListPublic>(
    `/posts/${encodeURIComponent(slug)}/comments${buildQuery(params)}`
  );
}

export function createComment(slug: string, data: CommentCreate) {
  return api.post<CommentPublic>(`/posts/${encodeURIComponent(slug)}/comments`, data);
}
