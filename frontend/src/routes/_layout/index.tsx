import { useQuery } from "@tanstack/react-query"
import {
  createFileRoute,
  Link as RouterLink,
  useNavigate,
} from "@tanstack/react-router"
import { MessageSquare, Plus, Search } from "lucide-react"
import { useState } from "react"

import { AuthorService } from "@/client"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - FastAPI Template",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const navigate = useNavigate()
  const [query, setQuery] = useState("")

  const { data, isLoading } = useQuery({
    queryKey: ["animes", "recent"],
    queryFn: () => AuthorService.listAnimes({ limit: 6 }),
  })

  const goSearch = (e: React.FormEvent) => {
    e.preventDefault()
    navigate({ to: "/admin/content", search: { q: query || undefined } })
  }

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-2xl truncate max-w-sm">
          Hi, {currentUser?.full_name || currentUser?.email} 👋
        </h1>
        <p className="text-muted-foreground">What are we adding today?</p>
      </div>

      <form onSubmit={goSearch} className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Jump to an anime..."
          className="pl-9"
          autoComplete="off"
        />
      </form>

      <div className="grid grid-cols-2 gap-2">
        <RouterLink
          to="/admin/content/new"
          className="flex items-center gap-2 rounded-lg border bg-card p-3 text-sm font-medium hover:bg-accent"
        >
          <Plus className="size-4 text-primary" />
          New Anime
        </RouterLink>
        <RouterLink
          to="/admin/comments"
          className="flex items-center gap-2 rounded-lg border bg-card p-3 text-sm font-medium hover:bg-accent"
        >
          <MessageSquare className="size-4 text-primary" />
          Comments
        </RouterLink>
      </div>

      <div className="flex flex-col gap-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Your anime
        </p>
        {isLoading ? (
          <div className="grid grid-cols-3 gap-2">
            {Array.from({ length: 6 }, (_, i) => i).map((i) => (
              <Skeleton key={i} className="aspect-2/3 w-full rounded-lg" />
            ))}
          </div>
        ) : data && data.data.length > 0 ? (
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
            {data.data.map((anime) => (
              <RouterLink
                key={anime.anime_id}
                to="/admin/content/$animeId"
                params={{ animeId: String(anime.anime_id) }}
                className="flex flex-col gap-1"
              >
                <img
                  src={anime.poster.mid}
                  alt=""
                  className="aspect-2/3 w-full rounded-lg object-cover bg-muted"
                  loading="lazy"
                />
                <span className="truncate text-xs font-medium">
                  {anime.anime_name}
                </span>
              </RouterLink>
            ))}
          </div>
        ) : (
          <p className="py-6 text-center text-sm text-muted-foreground">
            No anime yet -{" "}
            <RouterLink
              to="/admin/content/new"
              className="text-primary hover:underline"
            >
              add your first one
            </RouterLink>
            .
          </p>
        )}
        <RouterLink
          to="/admin/content"
          className="text-sm text-primary hover:underline"
        >
          Browse all content →
        </RouterLink>
      </div>
    </div>
  )
}
