import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Check, ExternalLink, ShieldAlert, Trash2 } from "lucide-react"
import { useState } from "react"

import { type AdminCommentPublic, AuthorService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const BLOG_URL = import.meta.env.VITE_BLOG_URL || "http://localhost:3000"

type StatusFilter = "pending" | "approved" | "spam"

// Comment moderation is author-scoped on the backend (any author tier, not
// just superusers) - see app/api/routes/author/comments.py. No extra gate
// needed here beyond _layout.tsx's own login check.
export const Route = createFileRoute("/_layout/admin/comments")({
  component: AdminComments,
  head: () => ({
    meta: [{ title: "Comments - Deadtoons Admin" }],
  }),
})

function statusBadgeVariant(status: string) {
  if (status === "approved") return "default"
  if (status === "spam") return "destructive"
  return "secondary"
}

function AdminComments() {
  const [status, setStatus] = useState<StatusFilter>("pending")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data, isLoading } = useQuery({
    queryKey: ["admin-comments", status],
    queryFn: () => AuthorService.listComments({ status, limit: 100 }),
  })

  const updateStatus = useMutation({
    mutationFn: ({
      commentId,
      newStatus,
    }: {
      commentId: number
      newStatus: "approved" | "spam"
    }) =>
      AuthorService.updateCommentStatus({
        commentId,
        requestBody: { status: newStatus },
      }),
    onSuccess: () => {
      showSuccessToast("Comment status updated")
      queryClient.invalidateQueries({ queryKey: ["admin-comments"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const deleteComment = useMutation({
    mutationFn: (commentId: number) =>
      AuthorService.deleteComment({ commentId }),
    onSuccess: () => {
      showSuccessToast("Comment deleted")
      queryClient.invalidateQueries({ queryKey: ["admin-comments"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const comments = data?.data ?? []

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Comments</h1>
        <p className="text-muted-foreground">
          Moderate blog post comments before they go live
        </p>
      </div>

      <Tabs
        value={status}
        onValueChange={(value) => setStatus(value as StatusFilter)}
      >
        <TabsList>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="approved">Approved</TabsTrigger>
          <TabsTrigger value="spam">Spam</TabsTrigger>
        </TabsList>
      </Tabs>

      {isLoading ? (
        <p className="text-muted-foreground text-sm">Loading...</p>
      ) : comments.length === 0 ? (
        <p className="text-muted-foreground text-sm">No comments here.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {comments.map((comment: AdminCommentPublic) => (
            <div
              key={comment.id}
              className="border rounded-lg p-4 flex flex-col gap-2 min-w-0"
            >
              <div className="flex items-start justify-between gap-2 min-w-0">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="font-medium truncate max-w-full">
                      {comment.author_name}
                    </span>
                    <Badge variant={statusBadgeVariant(comment.status)}>
                      {comment.status}
                    </Badge>
                  </div>
                  <p className="text-muted-foreground text-xs truncate">
                    {comment.author_email}
                  </p>
                </div>
                <span className="text-muted-foreground text-xs shrink-0">
                  {new Date(comment.created_at).toLocaleString()}
                </span>
              </div>

              <p className="text-sm whitespace-pre-wrap">{comment.body}</p>

              <div className="flex flex-col gap-2 mt-1 sm:flex-row sm:items-center sm:justify-between">
                <a
                  href={`${BLOG_URL}/posts/${comment.post_slug}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="min-w-0 truncate text-xs text-muted-foreground hover:text-foreground inline-flex items-center gap-1"
                >
                  <span className="truncate">{comment.post_title}</span>
                  <ExternalLink className="size-3 shrink-0" />
                </a>

                <div className="flex flex-wrap items-center gap-2">
                  {comment.status !== "approved" && (
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={updateStatus.isPending}
                      onClick={() =>
                        updateStatus.mutate({
                          commentId: comment.id,
                          newStatus: "approved",
                        })
                      }
                    >
                      <Check />
                      <span className="hidden sm:inline">Approve</span>
                    </Button>
                  )}
                  {comment.status !== "spam" && (
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={updateStatus.isPending}
                      onClick={() =>
                        updateStatus.mutate({
                          commentId: comment.id,
                          newStatus: "spam",
                        })
                      }
                    >
                      <ShieldAlert />
                      <span className="hidden sm:inline">Mark Spam</span>
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="destructive"
                    disabled={deleteComment.isPending}
                    onClick={() => deleteComment.mutate(comment.id)}
                  >
                    <Trash2 />
                    <span className="hidden sm:inline">Delete</span>
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
