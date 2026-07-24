import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { Upload } from "lucide-react"
import { useRef, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  AuthorService,
  type SeasonCreate,
  type TmdbSeasonSummary,
} from "@/client"
import { PageHeader } from "@/components/Common/PageHeader"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

export const Route = createFileRoute(
  "/_layout/admin/content/$animeId/seasons/new",
)({
  component: NewSeason,
})

const formSchema = z.object({
  season_number: z.number().int().positive("Required"),
  season_name: z.string().min(1, "Required"),
  total_episodes: z.number().int().positive("Required"),
  season_overview: z.string().min(1, "Required"),
  poster_source: z.enum(["tmdb", "bucket"]).nullable(),
  poster_img: z.string().nullable(),
  season_tmdb_id: z.string().nullable(),
  season_rel_date: z.string().nullable(),
})

type FormData = z.infer<typeof formSchema>

function NewSeason() {
  const { animeId } = Route.useParams()
  const navigate = useNavigate()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { data: anime } = useQuery({
    queryKey: ["anime", animeId],
    queryFn: () => AuthorService.getAnime({ animeId: Number(animeId) }),
  })

  const { data: show } = useQuery({
    queryKey: ["tmdb-show", anime?.anime_tmdb_id],
    queryFn: () =>
      AuthorService.getTvShow({ tmdbId: anime?.anime_tmdb_id as number }),
    enabled: !!anime?.anime_tmdb_id,
  })

  const [mode, setMode] = useState<"tmdb" | "manual">("tmdb")
  const [pickedTmdbId, setPickedTmdbId] = useState<string | null>(null)
  const [posterPreview, setPosterPreview] = useState<string | null>(null)

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    defaultValues: {
      season_number: (anime?.seasons.length ?? 0) + 1,
      season_name: "",
      total_episodes: 12,
      season_overview: "",
      poster_source: null,
      poster_img: null,
      season_tmdb_id: null,
      season_rel_date: null,
    },
  })

  const seasonDetailMutation = useMutation({
    mutationFn: (seasonTmdbId: string) =>
      AuthorService.getTvSeason({ seasonTmdbId }),
    onSuccess: (detail) => {
      setPickedTmdbId(detail.id)
      form.setValue("season_number", detail.season_number)
      form.setValue("season_name", detail.name)
      form.setValue("season_overview", detail.overview || anime?.overview || "")
      form.setValue("total_episodes", detail.episodes.length || 1)
      form.setValue("season_tmdb_id", detail.id)
      form.setValue("season_rel_date", detail.air_date)
      if (detail.poster_path) {
        form.setValue("poster_source", "tmdb")
        form.setValue("poster_img", detail.poster_path)
        setPosterPreview(detail.poster.mid)
      }
      form.clearErrors()
    },
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) =>
      AuthorService.createImage({
        formData: { file: file as unknown as string, kind: "poster" },
      }),
    onSuccess: (res, file) => {
      form.setValue("poster_source", "bucket")
      form.setValue("poster_img", res.image)
      setPosterPreview(URL.createObjectURL(file))
    },
    onError: handleError.bind(showErrorToast),
  })

  const createMutation = useMutation({
    mutationFn: (body: SeasonCreate) =>
      AuthorService.createSeason({
        animeId: Number(animeId),
        requestBody: body,
      }),
    onSuccess: (season) => {
      showSuccessToast("Season created")
      navigate({
        to: "/admin/content/$animeId/seasons/$seasonId",
        params: { animeId, seasonId: String(season.season_id) },
      })
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => {
    if (!data.poster_source || !data.poster_img) {
      form.setError("poster_img", { message: "Poster is required" })
      return
    }
    createMutation.mutate({
      season_number: data.season_number,
      season_name: data.season_name,
      total_episodes: data.total_episodes,
      season_overview: data.season_overview,
      poster_source: data.poster_source,
      poster_img: data.poster_img,
      season_tmdb_id: data.season_tmdb_id ?? undefined,
      season_rel_date: data.season_rel_date ?? undefined,
    })
  }

  return (
    <div className="flex flex-col gap-4 pb-8">
      <PageHeader
        title="New Season"
        subtitle={anime?.anime_name}
        backTo="/admin/content/$animeId"
      />

      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col gap-5"
      >
        {anime?.anime_tmdb_id && (
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

        {mode === "tmdb" && anime?.anime_tmdb_id ? (
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
            {show?.seasons.map((s: TmdbSeasonSummary) => (
              <button
                key={s.id}
                type="button"
                onClick={() => seasonDetailMutation.mutate(s.id)}
                className={cn(
                  "flex flex-col gap-1 rounded-lg border p-1 text-left transition-colors hover:border-primary",
                  pickedTmdbId === s.id && "border-primary ring-1 ring-primary",
                )}
              >
                <img
                  src={s.poster.mid}
                  alt=""
                  className="aspect-2/3 w-full rounded object-cover bg-muted"
                  loading="lazy"
                />
                <span className="truncate text-xs font-medium">{s.name}</span>
                <span className="text-[10px] text-muted-foreground">
                  {s.episode_count} episodes
                </span>
              </button>
            ))}
          </div>
        ) : (
          <div className="flex flex-col gap-1.5">
            <Label>Poster</Label>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) uploadMutation.mutate(file)
              }}
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex h-32 w-24 items-center justify-center overflow-hidden rounded-lg border border-dashed bg-muted/40 text-muted-foreground hover:bg-muted/70"
            >
              {posterPreview ? (
                <img
                  src={posterPreview}
                  alt=""
                  className="h-full w-full object-cover"
                />
              ) : uploadMutation.isPending ? (
                <span className="text-xs">Uploading...</span>
              ) : (
                <Upload className="size-4" />
              )}
            </button>
          </div>
        )}
        {form.formState.errors.poster_img && (
          <p className="text-sm text-destructive">
            {form.formState.errors.poster_img.message}
          </p>
        )}

        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="season_number">
              Season # <span className="text-destructive">*</span>
            </Label>
            <Input
              id="season_number"
              type="number"
              {...form.register("season_number", { valueAsNumber: true })}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="total_episodes">
              Total episodes <span className="text-destructive">*</span>
            </Label>
            <Input
              id="total_episodes"
              type="number"
              {...form.register("total_episodes", { valueAsNumber: true })}
            />
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="season_name">
            Name <span className="text-destructive">*</span>
          </Label>
          <Input id="season_name" {...form.register("season_name")} />
          {form.formState.errors.season_name && (
            <p className="text-sm text-destructive">
              {form.formState.errors.season_name.message}
            </p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="season_overview">
            Overview <span className="text-destructive">*</span>
          </Label>
          <Textarea
            id="season_overview"
            rows={4}
            {...form.register("season_overview")}
          />
          {form.formState.errors.season_overview && (
            <p className="text-sm text-destructive">
              {form.formState.errors.season_overview.message}
            </p>
          )}
        </div>

        <LoadingButton
          type="submit"
          loading={createMutation.isPending}
          className="mt-2"
        >
          Create Season
        </LoadingButton>
      </form>
    </div>
  )
}
