import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus, Trash2 } from "lucide-react"
import { type ReactNode, useState } from "react"

import {
  AuthorService,
  type EpisodeCreateItem,
  type TmdbEpisodeSummary,
} from "@/client"
import {
  ResponsiveSheet,
  ResponsiveSheetContent,
  ResponsiveSheetDescription,
  ResponsiveSheetFooter,
  ResponsiveSheetHeader,
  ResponsiveSheetTitle,
  ResponsiveSheetTrigger,
} from "@/components/Common/ResponsiveSheet"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface AddEpisodesDrawerProps {
  seasonId: number
  seasonTmdbId: string | null
  existingNumbers: number[]
  trigger: ReactNode
}

type ManualRow = { episode_number: number; episode_name: string }

export function AddEpisodesDrawer({
  seasonId,
  seasonTmdbId,
  existingNumbers,
  trigger,
}: AddEpisodesDrawerProps) {
  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState<"tmdb" | "manual">(
    seasonTmdbId ? "tmdb" : "manual",
  )
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [rows, setRows] = useState<ManualRow[]>([
    {
      episode_number: (existingNumbers[existingNumbers.length - 1] ?? 0) + 1,
      episode_name: "",
    },
  ])
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: tmdbSeason, isLoading: tmdbLoading } = useQuery({
    queryKey: ["tmdb-season-detail", seasonTmdbId],
    queryFn: () =>
      AuthorService.getTvSeason({ seasonTmdbId: seasonTmdbId as string }),
    enabled: open && mode === "tmdb" && !!seasonTmdbId,
  })

  const availableTmdbEpisodes = (tmdbSeason?.episodes ?? []).filter(
    (e) => !existingNumbers.includes(e.episode_number),
  )

  const toggle = (num: number) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(num)) next.delete(num)
      else next.add(num)
      return next
    })
  }

  const createMutation = useMutation({
    mutationFn: (episodes: EpisodeCreateItem[]) =>
      AuthorService.createEpisodes({ seasonId, requestBody: { episodes } }),
    onSuccess: (res) => {
      showSuccessToast(
        `${res.data.length} episode${res.data.length === 1 ? "" : "s"} added`,
      )
      queryClient.invalidateQueries({ queryKey: ["episodes", seasonId] })
      setOpen(false)
      setSelected(new Set())
    },
    onError: handleError.bind(showErrorToast),
  })

  const submitTmdb = () => {
    const episodes: EpisodeCreateItem[] = availableTmdbEpisodes
      .filter((e) => selected.has(e.episode_number))
      .map((e: TmdbEpisodeSummary) => ({
        episode_number: e.episode_number,
        episode_name: e.name,
        overview: e.overview,
        img: e.still_path,
        air_date: e.air_date,
        episode_runtime: e.runtime,
        episode_rating: e.rating,
        episode_tmdb_id: e.id,
      }))
    if (episodes.length === 0) return
    createMutation.mutate(episodes)
  }

  const submitManual = () => {
    const episodes: EpisodeCreateItem[] = rows
      .filter((r) => r.episode_number > 0)
      .map((r) => ({
        episode_number: r.episode_number,
        episode_name: r.episode_name || undefined,
      }))
    if (episodes.length === 0) return
    createMutation.mutate(episodes)
  }

  return (
    <ResponsiveSheet open={open} onOpenChange={setOpen}>
      <ResponsiveSheetTrigger asChild>{trigger}</ResponsiveSheetTrigger>
      <ResponsiveSheetContent>
        <ResponsiveSheetHeader>
          <ResponsiveSheetTitle>Add Episodes</ResponsiveSheetTitle>
          <ResponsiveSheetDescription>
            {seasonTmdbId
              ? "Import from TMDB, or add rows manually."
              : "Add episode rows manually - this season has no TMDB match."}
          </ResponsiveSheetDescription>
        </ResponsiveSheetHeader>

        <div className="flex flex-col gap-3 overflow-y-auto px-4 pb-4">
          {seasonTmdbId && (
            <Tabs
              value={mode}
              onValueChange={(v) => setMode(v as "tmdb" | "manual")}
            >
              <TabsList className="w-full">
                <TabsTrigger value="tmdb" className="flex-1">
                  From TMDB
                </TabsTrigger>
                <TabsTrigger value="manual" className="flex-1">
                  Manual
                </TabsTrigger>
              </TabsList>
            </Tabs>
          )}

          {mode === "tmdb" && seasonTmdbId ? (
            tmdbLoading ? (
              <p className="text-sm text-muted-foreground">
                Loading TMDB episodes...
              </p>
            ) : availableTmdbEpisodes.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No new episodes on TMDB - everything's already added.
              </p>
            ) : (
              <div className="flex flex-col gap-1">
                {availableTmdbEpisodes.map((e) => (
                  <button
                    key={e.id}
                    type="button"
                    onClick={() => toggle(e.episode_number)}
                    className="flex items-center gap-3 rounded-lg border p-2 text-left"
                  >
                    <Checkbox
                      checked={selected.has(e.episode_number)}
                      className="pointer-events-none"
                      tabIndex={-1}
                    />
                    <img
                      src={e.still.low}
                      alt=""
                      className="h-10 w-16 shrink-0 rounded object-cover bg-muted"
                      loading="lazy"
                    />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">
                        E{e.episode_number} - {e.name}
                      </p>
                      {e.air_date && (
                        <p className="text-xs text-muted-foreground">
                          {e.air_date}
                        </p>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )
          ) : (
            <div className="flex flex-col gap-2">
              {rows.map((row, i) => (
                <div key={`row-${i}`} className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={row.episode_number}
                    onChange={(e) => {
                      const v = Number(e.target.value)
                      setRows((prev) =>
                        prev.map((r, idx) =>
                          idx === i ? { ...r, episode_number: v } : r,
                        ),
                      )
                    }}
                    className="w-20"
                    aria-label="Episode number"
                  />
                  <Input
                    value={row.episode_name}
                    onChange={(e) => {
                      const v = e.target.value
                      setRows((prev) =>
                        prev.map((r, idx) =>
                          idx === i ? { ...r, episode_name: v } : r,
                        ),
                      )
                    }}
                    placeholder="Episode name (optional)"
                    className="flex-1"
                  />
                  <button
                    type="button"
                    onClick={() =>
                      setRows((prev) => prev.filter((_, idx) => idx !== i))
                    }
                    className="flex size-8 shrink-0 items-center justify-center rounded-full text-muted-foreground hover:bg-accent hover:text-destructive"
                    aria-label="Remove row"
                  >
                    <Trash2 className="size-4" />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={() =>
                  setRows((prev) => [
                    ...prev,
                    {
                      episode_number:
                        (prev[prev.length - 1]?.episode_number ?? 0) + 1,
                      episode_name: "",
                    },
                  ])
                }
                className="flex items-center justify-center gap-1 rounded-lg border border-dashed p-2 text-sm text-muted-foreground hover:bg-accent"
              >
                <Plus className="size-4" /> Add row
              </button>
            </div>
          )}
        </div>

        <ResponsiveSheetFooter>
          <LoadingButton
            loading={createMutation.isPending}
            onClick={mode === "tmdb" ? submitTmdb : submitManual}
            disabled={mode === "tmdb" && selected.size === 0}
          >
            {mode === "tmdb" && selected.size > 0
              ? `Add ${selected.size} Episode${selected.size === 1 ? "" : "s"}`
              : "Add Episodes"}
          </LoadingButton>
        </ResponsiveSheetFooter>
      </ResponsiveSheetContent>
    </ResponsiveSheet>
  )
}
