import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { Search, Upload } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { Controller, useForm } from "react-hook-form"
import { z } from "zod"

import {
  AdminService,
  type AnimeCreate,
  AuthorService,
  type TmdbMovieDetail,
  type TmdbSearchResult,
  type TmdbShowDetail,
} from "@/client"
import { PageHeader } from "@/components/Common/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { useDebouncedValue } from "@/hooks/useDebouncedValue"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/admin/content/new")({
  component: NewAnime,
  head: () => ({
    meta: [{ title: "New Anime - Deadtoons Admin" }],
  }),
})

const formSchema = z.object({
  anime_name: z.string().min(1, "Required"),
  type: z.enum(["movie", "tv"]),
  overview: z.string().min(1, "Required"),
  duration: z.number().int().positive("Required"),
  rating: z.string().min(1, "Required"),
  age_id: z.number().int().positive("Required"),
  anime_tmdb_id: z.number().nullable(),
  anime_rel_date: z.string().nullable(),
  genre_ids: z.array(z.number()),
  poster_source: z.enum(["tmdb", "bucket"]).nullable(),
  poster_img: z.string().nullable(),
  backdrop_source: z.enum(["tmdb", "bucket"]).nullable(),
  backdrop_img: z.string().nullable(),
})

type FormData = z.infer<typeof formSchema>

function TmdbSearchTab({
  animeType,
  onPick,
}: {
  animeType: "movie" | "tv"
  onPick: (detail: TmdbShowDetail | TmdbMovieDetail) => void
}) {
  const [query, setQuery] = useState("")
  const debouncedQuery = useDebouncedValue(query, 400)
  const [pickedId, setPickedId] = useState<number | null>(null)

  const { data, isFetching } = useQuery({
    queryKey: ["tmdb-search", debouncedQuery, animeType],
    queryFn: () =>
      AuthorService.searchTmdb({ query: debouncedQuery, type: animeType }),
    enabled: debouncedQuery.length > 1,
  })

  const detailMutation = useMutation<
    TmdbShowDetail | TmdbMovieDetail,
    Error,
    number
  >({
    mutationFn: async (tmdbId: number) =>
      animeType === "tv"
        ? await AuthorService.getTvShow({ tmdbId })
        : await AuthorService.getMovie({ tmdbId }),
    onSuccess: (detail) => {
      setPickedId(detail.tmdb_id)
      onPick(detail)
    },
  })

  const results = data?.results ?? []

  return (
    <div className="flex flex-col gap-3">
      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Search TMDB for a ${animeType === "tv" ? "show" : "movie"}...`}
          className="pl-9"
          autoComplete="off"
        />
      </div>

      {isFetching && (
        <p className="text-sm text-muted-foreground">Searching...</p>
      )}

      {!isFetching && debouncedQuery.length > 1 && results.length === 0 && (
        <p className="text-sm text-muted-foreground">No matches on TMDB.</p>
      )}

      {results.length > 0 && (
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
          {results.map((r: TmdbSearchResult) => (
            <button
              key={r.tmdb_id}
              type="button"
              onClick={() => detailMutation.mutate(r.tmdb_id)}
              className={cn(
                "flex flex-col gap-1 rounded-lg border p-1 text-left transition-colors hover:border-primary",
                pickedId === r.tmdb_id && "border-primary ring-1 ring-primary",
              )}
            >
              <img
                src={r.poster.mid}
                alt=""
                className="aspect-2/3 w-full rounded object-cover bg-muted"
                loading="lazy"
              />
              <span className="truncate text-xs font-medium">{r.title}</span>
            </button>
          ))}
        </div>
      )}

      {pickedId && (
        <p className="text-sm text-primary">
          Selected - fields below are pre-filled. Review and adjust as needed.
        </p>
      )}
    </div>
  )
}

function ManualImageField({
  label,
  onUploaded,
  previewUrl,
}: {
  label: string
  onUploaded: (key: string, previewUrl: string) => void
  previewUrl: string | null
}) {
  const inputRef = useRef<HTMLInputElement>(null)
  const { showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (file: File) =>
      AuthorService.createImage({
        formData: {
          file: file as unknown as string,
          kind: label.toLowerCase() as "poster" | "backdrop",
        },
      }),
    onSuccess: (res, file) => {
      onUploaded(res.image, URL.createObjectURL(file))
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="flex flex-col gap-1.5">
      <Label>{label}</Label>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) mutation.mutate(file)
        }}
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="flex h-28 w-full items-center justify-center overflow-hidden rounded-lg border border-dashed bg-muted/40 text-muted-foreground hover:bg-muted/70"
      >
        {previewUrl ? (
          <img src={previewUrl} alt="" className="h-full w-full object-cover" />
        ) : mutation.isPending ? (
          <span className="text-xs">Uploading...</span>
        ) : (
          <span className="flex flex-col items-center gap-1 text-xs">
            <Upload className="size-4" />
            Upload {label.toLowerCase()}
          </span>
        )}
      </button>
    </div>
  )
}

function NewAnime() {
  const navigate = useNavigate()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: ageRatings } = useQuery({
    queryKey: ["age-ratings"],
    queryFn: () => AdminService.listAgeRatings(),
  })
  const { data: genres } = useQuery({
    queryKey: ["genres"],
    queryFn: () => AdminService.listGenres(),
  })

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      anime_name: "",
      type: "tv",
      overview: "",
      duration: 24,
      rating: "",
      age_id: 0,
      anime_tmdb_id: null,
      anime_rel_date: null,
      genre_ids: [],
      poster_source: null,
      poster_img: null,
      backdrop_source: null,
      backdrop_img: null,
    },
  })

  const animeType = form.watch("type")
  const [mode, setMode] = useState<"tmdb" | "manual">("tmdb")
  const [posterPreview, setPosterPreview] = useState<string | null>(null)
  const [backdropPreview, setBackdropPreview] = useState<string | null>(null)

  // Switching movie/tv mid-search invalidates whatever was picked - the
  // detail shape (and duration semantics) differs between the two.
  useEffect(() => {
    form.setValue("anime_tmdb_id", null)
  }, [form])

  const applyTmdbDetail = (detail: TmdbShowDetail | TmdbMovieDetail) => {
    const isMovie = "title" in detail && "runtime" in detail
    form.setValue("anime_name", detail.title)
    form.setValue("overview", detail.overview)
    form.setValue("rating", detail.rating.toFixed(1))
    form.setValue("anime_tmdb_id", detail.tmdb_id)
    form.setValue(
      "anime_rel_date",
      isMovie
        ? (detail as TmdbMovieDetail).release_date
        : (detail as TmdbShowDetail).first_air_date,
    )
    if (isMovie && (detail as TmdbMovieDetail).runtime) {
      form.setValue("duration", (detail as TmdbMovieDetail).runtime as number)
    }
    if (detail.poster_path) {
      form.setValue("poster_source", "tmdb")
      form.setValue("poster_img", detail.poster_path)
      setPosterPreview(detail.poster.mid)
    }
    if (detail.backdrop_path) {
      form.setValue("backdrop_source", "tmdb")
      form.setValue("backdrop_img", detail.backdrop_path)
      setBackdropPreview(detail.backdrop.mid)
    }
    // Best-effort auto-map TMDB genre names onto our own genre ids.
    if (genres) {
      const matched = genres.data
        .filter((g) =>
          detail.genres.some(
            (name) => name.toLowerCase() === g.genre_name.toLowerCase(),
          ),
        )
        .map((g) => g.genre_id)
      form.setValue("genre_ids", matched)
    }
    form.clearErrors(["anime_name", "overview", "rating"])
  }

  const mutation = useMutation({
    mutationFn: (body: AnimeCreate) =>
      AuthorService.createAnime({ requestBody: body }),
    onSuccess: (anime) => {
      showSuccessToast("Anime created")
      navigate({
        to: "/admin/content/$animeId",
        params: { animeId: String(anime.anime_id) },
      })
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => {
    if (!data.poster_source || !data.poster_img) {
      form.setError("poster_img", { message: "Poster is required" })
      return
    }
    if (!data.backdrop_source || !data.backdrop_img) {
      form.setError("backdrop_img", { message: "Backdrop is required" })
      return
    }
    mutation.mutate({
      anime_name: data.anime_name,
      type: data.type,
      overview: data.overview,
      duration: data.duration,
      rating: data.rating,
      age_id: data.age_id,
      poster_source: data.poster_source,
      poster_img: data.poster_img,
      backdrop_source: data.backdrop_source,
      backdrop_img: data.backdrop_img,
      anime_tmdb_id: data.anime_tmdb_id ?? undefined,
      anime_rel_date: data.anime_rel_date ?? undefined,
      genre_ids: data.genre_ids,
    })
  }

  const genreIds = form.watch("genre_ids")

  return (
    <div className="flex flex-col gap-4 pb-8">
      <PageHeader title="New Anime" backTo="/admin/content" />

      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col gap-5"
      >
        <div>
          <Label className="mb-1.5 block">Type</Label>
          <Tabs
            value={animeType}
            onValueChange={(v) => form.setValue("type", v as "movie" | "tv")}
          >
            <TabsList className="w-full">
              <TabsTrigger value="tv" className="flex-1">
                TV Series
              </TabsTrigger>
              <TabsTrigger value="movie" className="flex-1">
                Movie
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

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

        {mode === "tmdb" ? (
          <TmdbSearchTab animeType={animeType} onPick={applyTmdbDetail} />
        ) : (
          <div className="grid grid-cols-2 gap-3">
            <ManualImageField
              label="Poster"
              previewUrl={posterPreview}
              onUploaded={(key, preview) => {
                form.setValue("poster_source", "bucket")
                form.setValue("poster_img", key)
                setPosterPreview(preview)
              }}
            />
            <ManualImageField
              label="Backdrop"
              previewUrl={backdropPreview}
              onUploaded={(key, preview) => {
                form.setValue("backdrop_source", "bucket")
                form.setValue("backdrop_img", key)
                setBackdropPreview(preview)
              }}
            />
          </div>
        )}
        {form.formState.errors.poster_img && (
          <p className="text-sm text-destructive">
            {form.formState.errors.poster_img.message}
          </p>
        )}

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="anime_name">
            Name <span className="text-destructive">*</span>
          </Label>
          <Input id="anime_name" {...form.register("anime_name")} />
          {form.formState.errors.anime_name && (
            <p className="text-sm text-destructive">
              {form.formState.errors.anime_name.message}
            </p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="overview">
            Overview <span className="text-destructive">*</span>
          </Label>
          <Textarea id="overview" rows={4} {...form.register("overview")} />
          {form.formState.errors.overview && (
            <p className="text-sm text-destructive">
              {form.formState.errors.overview.message}
            </p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="duration">
              Duration (min) <span className="text-destructive">*</span>
            </Label>
            <Input
              id="duration"
              type="number"
              {...form.register("duration", { valueAsNumber: true })}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="rating">
              Rating <span className="text-destructive">*</span>
            </Label>
            <Input
              id="rating"
              placeholder="e.g. 8.5"
              {...form.register("rating")}
            />
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label>
            Age rating <span className="text-destructive">*</span>
          </Label>
          <Controller
            control={form.control}
            name="age_id"
            render={({ field }) => (
              <Select
                value={field.value ? String(field.value) : ""}
                onValueChange={(v) => field.onChange(Number(v))}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select age rating" />
                </SelectTrigger>
                <SelectContent>
                  {ageRatings?.data.map((a) => (
                    <SelectItem key={a.age_id} value={String(a.age_id)}>
                      {a.age_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
          {form.formState.errors.age_id && (
            <p className="text-sm text-destructive">Required</p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <Label>Genres</Label>
          <div className="flex flex-wrap gap-1.5">
            {genres?.data.map((g) => {
              const selected = genreIds.includes(g.genre_id)
              return (
                <button
                  key={g.genre_id}
                  type="button"
                  onClick={() => {
                    form.setValue(
                      "genre_ids",
                      selected
                        ? genreIds.filter((id) => id !== g.genre_id)
                        : [...genreIds, g.genre_id],
                    )
                  }}
                >
                  <Badge variant={selected ? "default" : "outline"}>
                    {g.genre_name}
                  </Badge>
                </button>
              )
            })}
          </div>
        </div>

        <LoadingButton
          type="submit"
          loading={mutation.isPending}
          className="mt-2"
        >
          Create Anime
        </LoadingButton>
      </form>
    </div>
  )
}
