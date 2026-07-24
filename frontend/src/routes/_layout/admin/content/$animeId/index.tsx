import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  createFileRoute,
  Link as RouterLink,
  useNavigate,
} from "@tanstack/react-router"
import { Link2, Plus, Trash2, Tv } from "lucide-react"
import { useState } from "react"

import { AuthorService } from "@/client"
import { FabButton } from "@/components/Common/FabButton"
import { PageHeader } from "@/components/Common/PageHeader"
import { LinkManagerDrawer } from "@/components/Content/LinkManagerDrawer"
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
} from "@/components/ui/dialog"
import { LoadingButton } from "@/components/ui/loading-button"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/admin/content/$animeId/")({
  component: AnimeDetail,
})

function DeleteAnimeButton({
  animeId,
  animeName,
}: {
  animeId: number
  animeName: string
}) {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => AuthorService.deleteAnime({ animeId }),
    onSuccess: () => {
      showSuccessToast("Anime deleted")
      navigate({ to: "/admin/content" })
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button
        variant="ghost"
        size="icon"
        className="text-muted-foreground hover:text-destructive"
        onClick={() => setOpen(true)}
        aria-label="Delete anime"
      >
        <Trash2 className="size-4" />
      </Button>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete {animeName}?</DialogTitle>
          <DialogDescription>
            This permanently deletes the anime, every season, episode, pack and
            link under it. This cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>
              Cancel
            </Button>
          </DialogClose>
          <LoadingButton
            variant="destructive"
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            Delete
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function statusVariant(status: string) {
  return status === "completed" ? "secondary" : "default"
}

function AnimeDetail() {
  const { animeId } = Route.useParams()
  const queryClient = useQueryClient()

  const { data: anime, isLoading } = useQuery({
    queryKey: ["anime", animeId],
    queryFn: () => AuthorService.getAnime({ animeId: Number(animeId) }),
  })

  if (isLoading || !anime) {
    return (
      <div className="flex flex-col gap-4">
        <Skeleton className="h-40 w-full rounded-lg" />
        <Skeleton className="h-6 w-2/3" />
        <Skeleton className="h-4 w-1/3" />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4 pb-24">
      <PageHeader
        title={anime.anime_name}
        backTo="/admin/content"
        actions={
          <DeleteAnimeButton
            animeId={anime.anime_id}
            animeName={anime.anime_name}
          />
        }
      />

      <div className="flex gap-3">
        <img
          src={anime.poster.mid}
          alt=""
          className="h-32 w-22 shrink-0 rounded-lg object-cover bg-muted"
        />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-1.5">
            <Badge variant="secondary" className="uppercase">
              {anime.type}
            </Badge>
            <span className="text-sm text-muted-foreground">
              ★ {anime.rating}
            </span>
          </div>
          <div className="mt-1.5 flex flex-wrap gap-1">
            {anime.genres.map((g) => (
              <Badge key={g} variant="outline" className="text-[10px]">
                {g}
              </Badge>
            ))}
          </div>
          <p className="mt-2 line-clamp-4 text-sm text-muted-foreground">
            {anime.overview}
          </p>
        </div>
      </div>

      {anime.post_id && (
        <RouterLink
          to="/admin/posts/$postId"
          params={{ postId: String(anime.post_id) }}
          search={{ from: `/admin/content/${animeId}` }}
          className="text-sm text-primary hover:underline"
        >
          Edit blog post →
        </RouterLink>
      )}

      {anime.type === "movie" && anime.content_id ? (
        <div className="mt-2">
          <LinkManagerDrawer
            contentId={anime.content_id}
            title={`${anime.anime_name} - Links`}
            trigger={
              <Button className="w-full" variant="outline">
                <Link2 className="size-4" />
                Manage Links
              </Button>
            }
          />
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Seasons
          </p>
          {anime.seasons.length === 0 ? (
            <p className="py-6 text-center text-sm text-muted-foreground">
              No seasons yet - add the first one.
            </p>
          ) : (
            anime.seasons.map((season) => (
              <RouterLink
                key={season.season_id}
                to="/admin/content/$animeId/seasons/$seasonId"
                params={{ animeId, seasonId: String(season.season_id) }}
                className="flex items-center gap-3 rounded-lg border bg-card p-2 hover:bg-accent"
              >
                <img
                  src={season.poster.low}
                  alt=""
                  className="h-14 w-10 shrink-0 rounded object-cover bg-muted"
                  loading="lazy"
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium leading-tight">
                    {season.season_name}
                  </p>
                  <div className="mt-1 flex items-center gap-1.5">
                    <Badge
                      variant={statusVariant(season.status)}
                      className="text-[10px] capitalize"
                    >
                      {season.status}
                    </Badge>
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Tv className="size-3" />
                      {season.episode_count}/{season.total_episodes} episodes
                    </span>
                  </div>
                </div>
              </RouterLink>
            ))
          )}

          <FabButton asChild>
            <RouterLink
              to="/admin/content/$animeId/seasons/new"
              params={{ animeId }}
              onClick={() =>
                queryClient.invalidateQueries({ queryKey: ["anime", animeId] })
              }
            >
              <Plus />
              Add Season
            </RouterLink>
          </FabButton>
        </div>
      )}
    </div>
  )
}
