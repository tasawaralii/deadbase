import { api } from "@/lib/api";
import type { GenrePublic, TagPublic } from "@/lib/types";

export function getTags() {
  return api.get<TagPublic[]>("/tags");
}

export function getGenres() {
  return api.get<GenrePublic[]>("/genres");
}
