import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"
import { Plus, Search, Tv } from "lucide-react"
import { useState } from "react"

import { type AnimeAdminSummary, AuthorService } from "@/client"
import { FabButton } from "@/components/Common/FabButton"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useDebouncedValue } from "@/hooks/useDebouncedValue"

type TypeFilter = "all" | "movie" | "tv"

type ContentSearch = { q?: string }

export const Route = createFileRoute("/_layout/admin/content/")({
  component: ContentList,
  validateSearch: (search: Record<string, unknown>): ContentSearch =>
    typeof search.q === "string" ? { q: search.q } : {},
  head: () => ({
    meta: [{ title: "Content - Deadtoons Admin" }],
  }),
})

function AnimeRow({ anime }: { anime: AnimeAdminSummary }) {
  return (
    <RouterLink
      to="/admin/content/$animeId"
      params={{ animeId: String(anime.anime_id) }}
      className="flex items-center gap-3 rounded-lg border bg-card p-2 transition-colors hover:bg-accent"
    >
      <img
        src={anime.poster.low}
        alt=""
        className="h-16 w-11 shrink-0 rounded object-cover bg-muted"
        loading="lazy"
      />
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium leading-tight">{anime.anime_name}</p>
        <div className="mt-1 flex items-center gap-1.5">
          <Badge variant="secondary" className="text-[10px] uppercase">
            {anime.type}
          </Badge>
          {anime.type === "tv" && (
            <span className="flex items-center gap-1 text-xs text-muted-foreground">
              <Tv className="size-3" />
              {anime.season_count} season{anime.season_count === 1 ? "" : "s"}
            </span>
          )}
          {anime.rating && (
            <span className="text-xs text-muted-foreground">
              ★ {anime.rating}
            </span>
          )}
        </div>
      </div>
    </RouterLink>
  )
}

function ListSkeleton() {
  return (
    <div className="flex flex-col gap-2">
      {Array.from({ length: 8 }, (_, i) => i).map((i) => (
        <div key={i} className="flex items-center gap-3 rounded-lg border p-2">
          <Skeleton className="h-16 w-11 shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-3 w-1/3" />
          </div>
        </div>
      ))}
    </div>
  )
}

function ContentList() {
  const { q } = Route.useSearch()
  const [search, setSearch] = useState(q ?? "")
  const [type, setType] = useState<TypeFilter>("all")
  const debouncedSearch = useDebouncedValue(search, 300)

  const { data, isLoading } = useQuery({
    queryKey: ["animes", debouncedSearch, type],
    queryFn: () =>
      AuthorService.listAnimes({
        q: debouncedSearch || undefined,
        type: type === "all" ? undefined : type,
        limit: 100,
      }),
  })

  const animes = data?.data ?? []

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Content</h1>
        <p className="text-muted-foreground">
          {data
            ? `${data.count} title${data.count === 1 ? "" : "s"}`
            : "Anime library"}
        </p>
      </div>

      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search anime..."
          className="pl-9"
          autoComplete="off"
        />
      </div>

      <Tabs value={type} onValueChange={(v) => setType(v as TypeFilter)}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="tv">TV</TabsTrigger>
          <TabsTrigger value="movie">Movie</TabsTrigger>
        </TabsList>
      </Tabs>

      {isLoading ? (
        <ListSkeleton />
      ) : animes.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted-foreground">
          {debouncedSearch
            ? "No anime match that search."
            : "No anime yet - add your first one."}
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {animes.map((anime) => (
            <AnimeRow key={anime.anime_id} anime={anime} />
          ))}
        </div>
      )}

      <FabButton asChild>
        <RouterLink to="/admin/content/new">
          <Plus />
          New Anime
        </RouterLink>
      </FabButton>
    </div>
  )
}
