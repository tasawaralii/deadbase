import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Check, X } from "lucide-react"
import { type ReactNode, useState } from "react"

import { AuthorService, type LinkBatchResultItem } from "@/client"
import {
  ResponsiveSheet,
  ResponsiveSheetContent,
  ResponsiveSheetDescription,
  ResponsiveSheetHeader,
  ResponsiveSheetTitle,
  ResponsiveSheetTrigger,
} from "@/components/Common/ResponsiveSheet"
import { LoadingButton } from "@/components/ui/loading-button"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface SeasonLinksBatchDrawerProps {
  seasonId: number
  trigger: ReactNode
}

// Season-level batch: paste a folder link's files (or a list of file
// links), episode number is auto-detected from each filename server-side
// and matched to the episode with that number - no preview step exists on
// the backend, so this just submits and shows per-file results. A file
// that can't be matched creates nothing; a wrongly-matched file is fixed by
// deleting it from that episode's link manager and re-adding it directly
// there - not a manual-override control here (see the frontend plan).
export function SeasonLinksBatchDrawer({
  seasonId,
  trigger,
}: SeasonLinksBatchDrawerProps) {
  const [open, setOpen] = useState(false)
  const [paste, setPaste] = useState("")
  const [results, setResults] = useState<LinkBatchResultItem[] | null>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (urls: string[]) =>
      AuthorService.createSeasonLinksBatch({
        seasonId,
        requestBody: { gdrive_urls: urls },
      }),
    onSuccess: (res) => {
      setResults(res.results)
      const succeeded = res.results.filter((r) => r.success).length
      if (succeeded > 0) {
        showSuccessToast(
          `${succeeded} link${succeeded === 1 ? "" : "s"} matched and added`,
        )
        setPaste("")
      }
      queryClient.invalidateQueries({ queryKey: ["episodes", seasonId] })
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
    mutation.mutate(urls)
  }

  return (
    <ResponsiveSheet open={open} onOpenChange={setOpen}>
      <ResponsiveSheetTrigger asChild>{trigger}</ResponsiveSheetTrigger>
      <ResponsiveSheetContent>
        <ResponsiveSheetHeader>
          <ResponsiveSheetTitle>Add Links to Season</ResponsiveSheetTitle>
          <ResponsiveSheetDescription>
            Paste Google Drive file links, one per line. The episode number is
            read from each filename and matched automatically.
          </ResponsiveSheetDescription>
        </ResponsiveSheetHeader>

        <div className="flex flex-col gap-3 px-4 pb-4">
          <Textarea
            value={paste}
            onChange={(e) => setPaste(e.target.value)}
            placeholder={
              "https://drive.google.com/file/d/...\nhttps://drive.google.com/file/d/..."
            }
            rows={6}
          />
          <LoadingButton
            type="button"
            loading={mutation.isPending}
            disabled={!paste.trim()}
            onClick={handleAdd}
          >
            Match &amp; Add
          </LoadingButton>

          {results && (
            <div className="flex max-h-64 flex-col gap-1 overflow-y-auto rounded-lg border p-2">
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
        </div>
      </ResponsiveSheetContent>
    </ResponsiveSheet>
  )
}
