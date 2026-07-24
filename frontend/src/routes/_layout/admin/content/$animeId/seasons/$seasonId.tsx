import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { Link2, Lock, Plus, Trash2, X } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"

import { AdminService, AuthorService, type PackCreate } from "@/client"
import { PageHeader } from "@/components/Common/PageHeader"
import { AddEpisodesDrawer } from "@/components/Content/AddEpisodesDrawer"
import { LinkManagerDrawer } from "@/components/Content/LinkManagerDrawer"
import { SeasonLinksBatchDrawer } from "@/components/Content/SeasonLinksBatchDrawer"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute(
  "/_layout/admin/content/$animeId/seasons/$seasonId",
)({
  component: SeasonDetail,
})

function LinkCountBadge({ count }: { count: number }) {
  return (
    <Badge
      variant={count === 0 ? "destructive" : "secondary"}
      className="text-[10px]"
    >
      {count === 0 ? "No links" : `${count} link${count === 1 ? "" : "s"}`}
    </Badge>
  )
}

function AddPackDialog({
  seasonId,
  locked,
}: {
  seasonId: number
  locked: boolean
}) {
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<{ pack_name: string; start_ep: number; end_ep: number }>(
    {
      defaultValues: { pack_name: "", start_ep: 1, end_ep: 1 },
    },
  )

  const mutation = useMutation({
    mutationFn: (body: PackCreate) =>
      AuthorService.createPack({ seasonId, requestBody: body }),
    onSuccess: () => {
      showSuccessToast("Pack created")
      queryClient.invalidateQueries({ queryKey: ["packs", seasonId] })
      form.reset()
      setOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" disabled={locked}>
          <Plus className="size-4" /> Add Pack
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={form.handleSubmit((data) => mutation.mutate(data))}>
          <DialogHeader>
            <DialogTitle>Add Pack</DialogTitle>
            <DialogDescription>
              A bundle of episodes downloaded as one file.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-3 py-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium" htmlFor="pack_name">
                Name
              </label>
              <Input
                id="pack_name"
                {...form.register("pack_name", { required: true })}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium" htmlFor="start_ep">
                  Start ep
                </label>
                <Input
                  id="start_ep"
                  type="number"
                  {...form.register("start_ep", { valueAsNumber: true })}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium" htmlFor="end_ep">
                  End ep
                </label>
                <Input
                  id="end_ep"
                  type="number"
                  {...form.register("end_ep", { valueAsNumber: true })}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline" disabled={mutation.isPending}>
                Cancel
              </Button>
            </DialogClose>
            <LoadingButton type="submit" loading={mutation.isPending}>
              Create
            </LoadingButton>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

function DubsWidget({
  seasonId,
  locked,
}: {
  seasonId: number
  locked: boolean
}) {
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()
  const [ottId, setOttId] = useState<string>("")
  const [languageId, setLanguageId] = useState<string>("")

  const dubsQuery = useQuery({
    queryKey: ["dubs", seasonId],
    queryFn: () => AuthorService.listSeasonDubs({ seasonId }),
  })
  const ottQuery = useQuery({
    queryKey: ["ott-platforms"],
    queryFn: () => AdminService.listOttPlatforms(),
  })
  const languageQuery = useQuery({
    queryKey: ["languages"],
    queryFn: () => AdminService.listLanguages(),
  })

  const addMutation = useMutation({
    mutationFn: () =>
      AuthorService.addSeasonDub({
        seasonId,
        requestBody: { ott_id: Number(ottId), language_id: Number(languageId) },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dubs", seasonId] })
      setOttId("")
      setLanguageId("")
    },
    onError: handleError.bind(showErrorToast),
  })

  const removeMutation = useMutation({
    mutationFn: (vars: { ottId: number; languageId: number }) =>
      AuthorService.removeSeasonDub({
        seasonId,
        ottId: vars.ottId,
        languageId: vars.languageId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dubs", seasonId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Dubs
      </p>
      <div className="flex flex-wrap gap-1.5">
        {dubsQuery.data?.data.map((d) => (
          <Badge
            key={`${d.ott_id}-${d.language_id}`}
            variant="outline"
            className="gap-1 pr-1"
          >
            {d.ott_name} · {d.language_name}
            {!locked && (
              <button
                type="button"
                onClick={() =>
                  removeMutation.mutate({
                    ottId: d.ott_id,
                    languageId: d.language_id,
                  })
                }
                aria-label="Remove dub"
              >
                <X className="size-3" />
              </button>
            )}
          </Badge>
        ))}
        {dubsQuery.data?.data.length === 0 && (
          <span className="text-sm text-muted-foreground">No dubs added.</span>
        )}
      </div>
      {!locked && (
        <div className="flex items-center gap-2">
          <Select value={ottId} onValueChange={setOttId}>
            <SelectTrigger className="flex-1">
              <SelectValue placeholder="Platform" />
            </SelectTrigger>
            <SelectContent>
              {ottQuery.data?.data.map((o) => (
                <SelectItem key={o.ott_id} value={String(o.ott_id)}>
                  {o.ott_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={languageId} onValueChange={setLanguageId}>
            <SelectTrigger className="flex-1">
              <SelectValue placeholder="Language" />
            </SelectTrigger>
            <SelectContent>
              {languageQuery.data?.data.map((l) => (
                <SelectItem key={l.language_id} value={String(l.language_id)}>
                  {l.language_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            size="icon"
            variant="outline"
            disabled={!ottId || !languageId || addMutation.isPending}
            onClick={() => addMutation.mutate()}
            aria-label="Add dub"
          >
            <Plus className="size-4" />
          </Button>
        </div>
      )}
    </div>
  )
}

function SeasonDetail() {
  const { animeId, seasonId } = Route.useParams()
  const seasonIdNum = Number(seasonId)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [deleteOpen, setDeleteOpen] = useState(false)

  const { data: season, isLoading } = useQuery({
    queryKey: ["season", seasonId],
    queryFn: () => AuthorService.getSeason({ seasonId: seasonIdNum }),
  })
  const { data: episodesData } = useQuery({
    queryKey: ["episodes", seasonIdNum],
    queryFn: () => AuthorService.listEpisodes({ seasonId: seasonIdNum }),
  })
  const { data: packsData } = useQuery({
    queryKey: ["packs", seasonIdNum],
    queryFn: () => AuthorService.listPacks({ seasonId: seasonIdNum }),
  })

  const locked =
    !user?.is_superuser &&
    user?.access_scope === "ongoing" &&
    season?.status === "completed"

  const statusMutation = useMutation({
    mutationFn: (status: "ongoing" | "completed") =>
      AuthorService.updateSeason({
        seasonId: seasonIdNum,
        requestBody: { status },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["season", seasonId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const deleteMutation = useMutation({
    mutationFn: () => AuthorService.deleteSeason({ seasonId: seasonIdNum }),
    onSuccess: () => {
      showSuccessToast("Season deleted")
      navigate({ to: "/admin/content/$animeId", params: { animeId } })
    },
    onError: handleError.bind(showErrorToast),
  })

  if (isLoading || !season) {
    return (
      <div className="flex flex-col gap-4">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-24 w-full rounded-lg" />
      </div>
    )
  }

  const episodes = episodesData?.data ?? []
  const packs = packsData?.data ?? []

  return (
    <div className="flex flex-col gap-5 pb-24">
      <PageHeader
        title={season.season_name}
        backTo="/admin/content/$animeId"
        actions={
          <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
            <Button
              variant="ghost"
              size="icon"
              className="text-muted-foreground hover:text-destructive"
              onClick={() => setDeleteOpen(true)}
              aria-label="Delete season"
            >
              <Trash2 className="size-4" />
            </Button>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Delete {season.season_name}?</DialogTitle>
                <DialogDescription>
                  This permanently deletes the season, every episode, pack and
                  link under it. This cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="outline" disabled={deleteMutation.isPending}>
                    Cancel
                  </Button>
                </DialogClose>
                <LoadingButton
                  variant="destructive"
                  loading={deleteMutation.isPending}
                  onClick={() => deleteMutation.mutate()}
                >
                  Delete
                </LoadingButton>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      {locked && (
        <div className="flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-sm text-amber-700 dark:text-amber-400">
          <Lock className="size-4 shrink-0" />
          This season is marked completed - you can't edit it.
        </div>
      )}

      <button
        type="button"
        disabled={locked}
        onClick={() =>
          statusMutation.mutate(
            season.status === "ongoing" ? "completed" : "ongoing",
          )
        }
        className="self-start"
      >
        <Badge
          variant={season.status === "completed" ? "secondary" : "default"}
          className="cursor-pointer capitalize"
        >
          {season.status}
        </Badge>
      </button>

      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Episodes
          </p>
          <div className="flex gap-2">
            <SeasonLinksBatchDrawer
              seasonId={seasonIdNum}
              trigger={
                <Button variant="outline" size="sm" disabled={locked}>
                  <Link2 className="size-4" /> Add Links
                </Button>
              }
            />
            <AddEpisodesDrawer
              seasonId={seasonIdNum}
              seasonTmdbId={season.season_tmdb_id}
              existingNumbers={episodes.map((e) => e.episode_number)}
              trigger={
                <Button size="sm" disabled={locked}>
                  <Plus className="size-4" /> Add Episodes
                </Button>
              }
            />
          </div>
        </div>

        {episodes.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            No episodes yet.
          </p>
        ) : (
          <div className="flex flex-col gap-1.5">
            {episodes.map((ep) => (
              <LinkManagerDrawer
                key={ep.episode_id}
                contentId={ep.content_id}
                title={`Episode ${ep.episode_number} - Links`}
                trigger={
                  <button
                    type="button"
                    className="flex w-full items-center gap-3 rounded-lg border bg-card p-2 text-left hover:bg-accent"
                  >
                    <span className="flex size-9 shrink-0 items-center justify-center rounded-md bg-muted text-sm font-semibold">
                      {ep.episode_number}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">
                        {ep.episode_name || `Episode ${ep.episode_number}`}
                      </p>
                      {ep.air_date && (
                        <p className="text-xs text-muted-foreground">
                          {ep.air_date}
                        </p>
                      )}
                    </div>
                    <LinkCountBadge count={ep.link_count} />
                  </button>
                }
              />
            ))}
          </div>
        )}
      </div>

      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Packs
          </p>
          <AddPackDialog seasonId={seasonIdNum} locked={!!locked} />
        </div>
        {packs.length === 0 ? (
          <p className="py-4 text-center text-sm text-muted-foreground">
            No packs.
          </p>
        ) : (
          <div className="flex flex-col gap-1.5">
            {packs.map((pack) => (
              <LinkManagerDrawer
                key={pack.pack_id}
                contentId={pack.content_id}
                title={`${pack.pack_name} - Links`}
                trigger={
                  <button
                    type="button"
                    className="flex w-full items-center gap-3 rounded-lg border bg-card p-2 text-left hover:bg-accent"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">
                        {pack.pack_name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Episodes {pack.start_ep}-{pack.end_ep}
                      </p>
                    </div>
                    <LinkCountBadge count={pack.link_count} />
                  </button>
                }
              />
            ))}
          </div>
        )}
      </div>

      <DubsWidget seasonId={seasonIdNum} locked={!!locked} />
    </div>
  )
}
