import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { ExternalLink, Pin, Upload } from "lucide-react"
import { useEffect, useRef, useState } from "react"

import { AdminService, AuthorService } from "@/client"
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
import { Skeleton } from "@/components/ui/skeleton"
import { Switch } from "@/components/ui/switch"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const BLOG_URL = import.meta.env.VITE_BLOG_URL || "http://localhost:3000"

type PostSearch = { from?: string }

export const Route = createFileRoute("/_layout/admin/posts/$postId")({
  component: PostEditor,
  validateSearch: (search: Record<string, unknown>): PostSearch =>
    typeof search.from === "string" ? { from: search.from } : {},
  head: () => ({
    meta: [{ title: "Edit Post - Deadtoons Admin" }],
  }),
})

function PostEditor() {
  const { postId } = Route.useParams()
  const { from } = Route.useSearch()
  const postIdNum = Number(postId)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { data: post, isLoading } = useQuery({
    queryKey: ["post", postId],
    queryFn: () => AuthorService.getPost({ postId: postIdNum }),
  })
  const { data: allTags } = useQuery({
    queryKey: ["tags"],
    queryFn: () => AdminService.listTags(),
  })

  const [title, setTitle] = useState("")
  const [status, setStatus] = useState<"ongoing" | "completed">("ongoing")
  const [sticky, setSticky] = useState(false)
  const [backdropImg, setBackdropImg] = useState<string | null>(null)
  const [tagIds, setTagIds] = useState<number[]>([])
  const [hydrated, setHydrated] = useState(false)

  // Hydrate local form state once, when both the post and the tag catalog
  // (needed to map the post's tag slugs back to ids) have arrived.
  useEffect(() => {
    if (!post || !allTags || hydrated) return
    setTitle(post.title)
    setStatus(post.status)
    setSticky(post.sticky)
    setBackdropImg(post.backdrop_img)
    setTagIds(
      allTags.data
        .filter((t) => post.tags.some((pt) => pt.slug === t.slug))
        .map((t) => t.id),
    )
    setHydrated(true)
  }, [post, allTags, hydrated])

  const uploadMutation = useMutation({
    mutationFn: (file: File) =>
      AuthorService.createImage({
        formData: { file: file as unknown as string, kind: "backdrop" },
      }),
    onSuccess: (res) => {
      setBackdropImg(res.urls.high)
    },
    onError: handleError.bind(showErrorToast),
  })

  const saveMutation = useMutation({
    mutationFn: () =>
      AuthorService.updatePost({
        postId: postIdNum,
        requestBody: {
          title,
          backdrop_img: backdropImg,
          status,
          sticky,
          tag_ids: tagIds,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Post updated")
      queryClient.invalidateQueries({ queryKey: ["post", postId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  if (isLoading || !post) {
    return (
      <div className="flex flex-col gap-4">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-40 w-full rounded-lg" />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-5 pb-8">
      <PageHeader title="Edit Post" backTo={from ?? "/admin/content"} />

      <div className="flex flex-col gap-1.5">
        <Label>Backdrop</Label>
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
          className="flex h-36 w-full items-center justify-center overflow-hidden rounded-lg border border-dashed bg-muted/40 text-muted-foreground hover:bg-muted/70"
        >
          {uploadMutation.isPending ? (
            <span className="text-xs">Uploading...</span>
          ) : backdropImg ? (
            <img
              src={backdropImg}
              alt=""
              className="h-full w-full object-cover"
            />
          ) : (
            <span className="flex flex-col items-center gap-1 text-xs">
              <Upload className="size-4" />
              Upload backdrop
            </span>
          )}
        </button>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="post-title">Title</Label>
        <Input
          id="post-title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <Label>Slug</Label>
        <div className="rounded-md border bg-muted/40 px-3 py-2 text-sm text-muted-foreground">
          /{post.slug}
        </div>
        <p className="text-xs text-muted-foreground">
          Not editable - this is a public URL, changing it breaks bookmarks and
          search results.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1.5">
          <Label>Status</Label>
          <Select
            value={status}
            onValueChange={(v) => setStatus(v as typeof status)}
          >
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ongoing">Ongoing</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="post-sticky" className="flex items-center gap-1">
            <Pin className="size-3.5" /> Sticky
          </Label>
          <div className="flex h-9 items-center">
            <Switch
              id="post-sticky"
              checked={sticky}
              onCheckedChange={setSticky}
            />
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label>Tags</Label>
        <div className="flex flex-wrap gap-1.5">
          {allTags?.data.map((tag) => {
            const selected = tagIds.includes(tag.id)
            return (
              <button
                key={tag.id}
                type="button"
                onClick={() =>
                  setTagIds((prev) =>
                    selected
                      ? prev.filter((id) => id !== tag.id)
                      : [...prev, tag.id],
                  )
                }
              >
                <Badge variant={selected ? "default" : "outline"}>
                  {tag.name}
                </Badge>
              </button>
            )
          })}
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{post.views.toLocaleString()} views</span>
        <a
          href={`${BLOG_URL}/posts/${post.slug}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 hover:text-foreground"
        >
          View live <ExternalLink className="size-3" />
        </a>
      </div>

      <LoadingButton
        onClick={() => saveMutation.mutate()}
        loading={saveMutation.isPending}
        className="mt-2"
      >
        Save
      </LoadingButton>
    </div>
  )
}
