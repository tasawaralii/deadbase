import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  AnimeDetail,
  EpisodeDetail,
  Message,
  PackDetail,
  StartUnlockResponse,
  TrendingEpisodeList,
  UnlockStatus,
} from "@/lib/types";

export type TrendingWindow = "today" | "week" | "month" | "all";

export function useAnime(slug: string) {
  return useQuery({
    queryKey: ["anime", slug],
    queryFn: () => api.get<AnimeDetail>(`/anime/${slug}`),
    enabled: Boolean(slug),
  });
}

export function useEpisode(slug: string, season: number, episode: number) {
  return useQuery({
    queryKey: ["episode", slug, season, episode],
    queryFn: () => api.get<EpisodeDetail>(`/anime/${slug}/season/${season}/episode/${episode}`),
    enabled: Boolean(slug) && Number.isFinite(season) && Number.isFinite(episode),
  });
}

export function usePack(slug: string, season: number, startEp: number, endEp: number) {
  return useQuery({
    queryKey: ["pack", slug, season, startEp, endEp],
    queryFn: () => api.get<PackDetail>(`/anime/${slug}/season/${season}/pack/${startEp}-${endEp}`),
    enabled:
      Boolean(slug) &&
      Number.isFinite(season) &&
      Number.isFinite(startEp) &&
      Number.isFinite(endEp),
  });
}

export function useTrendingEpisodes(window: TrendingWindow, limit = 7) {
  return useQuery({
    queryKey: ["trending-episodes", window, limit],
    queryFn: () =>
      api.get<TrendingEpisodeList>(`/trending/episodes?window=${window}&limit=${limit}`),
  });
}

export function useUnlockStatus(linkServerId: number | null) {
  return useQuery({
    queryKey: ["unlock-status", linkServerId],
    queryFn: () => api.get<UnlockStatus>(`/unlock/${linkServerId}`),
    enabled: linkServerId != null,
    // The solve happens on the shortener's site in another tab/redirect -
    // refetch when the user comes back to this tab so progress is current.
    refetchOnWindowFocus: true,
  });
}

export function useStartUnlock(linkServerId: number | null) {
  return useMutation({
    mutationFn: (shortenerId: number) =>
      api.post<StartUnlockResponse>(`/unlock/${linkServerId}/start`, {
        shortener_id: shortenerId,
      }),
  });
}

export function useReportShortener(linkServerId: number | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (vars: { shortener_id: number; reason?: string }) =>
      api.post<Message>(`/unlock/${linkServerId}/report`, vars),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["unlock-status", linkServerId],
      });
    },
  });
}

export function useTrackView(contentId: number | null) {
  return useMutation({
    mutationFn: () => api.post<Message>(`/track/view/${contentId}`),
  });
}
