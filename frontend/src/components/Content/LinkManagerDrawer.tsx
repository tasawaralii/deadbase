import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Check, Link2, Trash2, X } from "lucide-react"
import { type ReactNode, useState } from "react"

import { AdminService, AuthorService, type LinkBatchResultItem } from "@/client"
import {
  ResponsiveSheet,
  ResponsiveSheetContent,
  ResponsiveSheetDescription,
  ResponsiveSheetHeader,
  ResponsiveSheetTitle,
  ResponsiveSheetTrigger,
} from "@/components/Common/ResponsiveSheet"
import { Badge } from "@/components/ui/badge"
import { LoadingButton } from "@/components/ui/loading-button"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface LinkManagerDrawerProps {
  contentId: number
  trigger: ReactNode
  title?: string
}

export function LinkManagerDrawer({
  contentId,
  trigger,
  title = "Links",
}: LinkManagerDrawerProps) {
  const [open, setOpen] = useState(false)
  const [paste, setPaste] = useState("")
  const [results, setResults] = useState<LinkBatchResultItem[] | null>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const linksQuery = useQuery({
    queryKey: ["links", contentId],
    queryFn: () => AuthorService.listLinks({ contentId }),
    enabled: open,
  })
  const qualitiesQuery = useQuery({
    queryKey: ["qualities"],
    queryFn: () => AdminService.listQualities(),
    enabled: open,
  })

  const addMutation = useMutation({
    mutationFn: (urls: string[]) =>
      AuthorService.createLinks({
        contentId,
        requestBody: { gdrive_urls: urls },
      }),
    onSuccess: (res) => {
      setResults(res.results)
      const succeeded = res.results.filter((r) => r.success).length
      if (succeeded > 0) {
        showSuccessToast(`${succeeded} link${succeeded === 1 ? "" : "s"} added`)
        setPaste("")
      }
      queryClient.invalidateQueries({ queryKey: ["links", contentId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const toggleLiveMutation = useMutation({
    mutationFn: ({ linkId, isLive }: { linkId: number; isLive: boolean }) =>
      AuthorService.updateLink({ linkId, requestBody: { is_live: isLive } }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["links", contentId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const deleteMutation = useMutation({
    mutationFn: (linkId: number) => AuthorService.deleteLink({ linkId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["links", contentId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const handleAdd = () => {
    const urls = paste
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean)
    if (urls.length === 0) return
    setResults(null)
    addMutation.mutate(urls)
  }

  const qualityName = (qualityId: number | null) => {
    if (qualityId == null) return null
    return qualitiesQuery.data?.data.find((q) => q.quality_id === qualityId)
      ?.quality_name
  }

  const links = linksQuery.data?.data ?? []

  return (
    <ResponsiveSheet open={open} onOpenChange={setOpen}>
      <ResponsiveSheetTrigger asChild>{trigger}</ResponsiveSheetTrigger>
      <ResponsiveSheetContent>
        <ResponsiveSheetHeader>
          <ResponsiveSheetTitle>{title}</ResponsiveSheetTitle>
          <ResponsiveSheetDescription>
            Paste one or more Google Drive file links, one per line.
          </ResponsiveSheetDescription>
        </ResponsiveSheetHeader>

        <div className="flex flex-col gap-3 overflow-y-auto px-4 pb-4">
          <Textarea
            value={paste}
            onChange={(e) => setPaste(e.target.value)}
            placeholder={
              "https://drive.google.com/file/d/...\nhttps://drive.google.com/file/d/..."
            }
            rows={4}
          />
          <LoadingButton
            type="button"
            loading={addMutation.isPending}
            disabled={!paste.trim()}
            onClick={handleAdd}
          >
            Add Links
          </LoadingButton>

          {results && (
            <div className="flex flex-col gap-1 rounded-lg border p-2">
              {results.map((r) => (
                <div
                  key={r.gdrive_url}
                  className="flex items-start gap-2 text-sm"
                >
                  {r.success ? (
                    <Check className="mt-0.5 size-4 shrink-0 text-green-600" />
                  ) : (
                    <X className="mt-0.5 size-4 shrink-0 text-destructive" />
                  )}
                  <span className="min-w-0 truncate">
                    {r.success ? r.link?.filename : r.error}
                  </span>
                </div>
              ))}
            </div>
          )}

          <div className="mt-2 flex flex-col gap-2">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Existing links
            </p>
            {linksQuery.isLoading ? (
              <p className="text-sm text-muted-foreground">Loading...</p>
            ) : links.length === 0 ? (
              <p className="flex items-center gap-2 text-sm text-muted-foreground">
                <Link2 className="size-4" />
                No links yet.
              </p>
            ) : (
              links.map((link) => (
                <div
                  key={link.link_id}
                  className="flex items-center gap-2 rounded-lg border p-2"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">
                      {link.filename}
                    </p>
                    <div className="mt-0.5 flex items-center gap-1.5">
                      {qualityName(link.quality_id) && (
                        <Badge variant="secondary" className="text-[10px]">
                          {qualityName(link.quality_id)}
                        </Badge>
                      )}
                      {link.size && (
                        <span className="text-xs text-muted-foreground">
                          {link.size}
                        </span>
                      )}
                    </div>
                  </div>
                  <Switch
                    checked={link.is_live}
                    onCheckedChange={(checked) =>
                      toggleLiveMutation.mutate({
                        linkId: link.link_id,
                        isLive: checked,
                      })
                    }
                    aria-label="Live"
                  />
                  <button
                    type="button"
                    onClick={() => deleteMutation.mutate(link.link_id)}
                    className="flex size-8 items-center justify-center rounded-full text-muted-foreground hover:bg-accent hover:text-destructive"
                    aria-label="Delete link"
                  >
                    <Trash2 className="size-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </ResponsiveSheetContent>
    </ResponsiveSheet>
  )
}
