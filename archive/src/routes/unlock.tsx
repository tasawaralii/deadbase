import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { z } from "zod";
import { AlertTriangle, Check, Crown, Download, HelpCircle, Loader2, X, Zap } from "lucide-react";
import { useReportShortener, useStartUnlock, useUnlockStatus } from "@/hooks/use-api";
import type { ShortenerOption } from "@/lib/types";
import { ApiError } from "@/lib/api";
import { Textarea } from "@/components/ui/textarea";

const unlockSearchSchema = z.object({
  link_server_id: z.coerce.number().optional().catch(undefined),
});

export const Route = createFileRoute("/unlock")({
  validateSearch: unlockSearchSchema,
  head: () => ({
    meta: [
      { title: "Unlock Downloads — Deadtoons" },
      {
        name: "description",
        content: "Solve a shortener link to unlock this download.",
      },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: DownloadUnlockGate,
});

function DownloadUnlockGate() {
  const { link_server_id } = Route.useSearch();
  const linkServerId = link_server_id ?? null;
  const { data: status, isLoading, isError, error } = useUnlockStatus(linkServerId);
  const startUnlock = useStartUnlock(linkServerId);
  const reportShortener = useReportShortener(linkServerId);

  const [infoTarget, setInfoTarget] = useState<ShortenerOption | null>(null);
  const [reportTarget, setReportTarget] = useState<ShortenerOption | null>(null);
  const [reportReason, setReportReason] = useState("Not working");
  const [reportDetails, setReportDetails] = useState("");

  const openReport = (shortener: ShortenerOption) => {
    setReportReason("Not working");
    setReportDetails("");
    setReportTarget(shortener);
  };

  if (linkServerId === null) {
    return (
      <main className="grid min-h-screen place-items-center bg-background px-4 text-center">
        <div>
          <h1 className="font-display text-2xl">No download selected</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Head back to an episode and pick a download mirror to unlock.
          </p>
        </div>
      </main>
    );
  }

  if (isLoading) {
    return (
      <main className="grid min-h-screen place-items-center bg-background px-4">
        <p className="label-cap text-muted-foreground">Loading…</p>
      </main>
    );
  }

  if (isError || !status) {
    const notFound = error instanceof ApiError && error.status === 404;
    return (
      <main className="grid min-h-screen place-items-center bg-background px-4 text-center">
        <div>
          <h1 className="font-display text-2xl">
            {notFound ? "Link not found" : "Something went wrong"}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {notFound
              ? "This download link doesn't exist or was removed."
              : "Please go back and try again."}
          </p>
        </div>
      </main>
    );
  }

  if (status.unlocked && status.url) {
    return (
      <main className="grid min-h-screen place-items-center bg-background px-4 text-center">
        <div className="panel max-w-sm overflow-hidden">
          <div className="bg-secondary px-4 py-3 text-secondary-foreground">
            <p className="label-cap">VIP Pass Active</p>
          </div>
          <div className="p-5">
            <Crown className="mx-auto h-10 w-10 text-accent" />
            <h1 className="mt-3 font-display text-2xl">You're unlocked</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Free downloads for the next 24 hours.
            </p>
            <a
              href={status.url}
              className="btn-base mt-5 w-full justify-center bg-primary py-3 text-primary-foreground"
            >
              <Download className="h-4 w-4" />
              Download now
            </a>
          </div>
        </div>
      </main>
    );
  }

  const shorteners = status.shorteners ?? [];
  const solvedCount = status.solved ?? 0;
  const total = status.required ?? shorteners.length;
  const remaining = Math.max(total - solvedCount, 0);
  const pct = total > 0 ? Math.round((solvedCount / total) * 100) : 0;
  const anyAvailable = shorteners.some((s) => !s.already_solved && !s.reported);

  const unlock = (shortener: ShortenerOption) => {
    startUnlock.mutate(shortener.id, {
      onSuccess: (data) => {
        window.location.href = data.redirect_url;
      },
    });
  };

  const submitReport = () => {
    if (!reportTarget) return;
    const details = reportDetails.trim();
    const reason = details ? `${reportReason}: ${details}` : reportReason;
    reportShortener.mutate(
      { shortener_id: reportTarget.id, reason },
      { onSuccess: () => setReportTarget(null) },
    );
  };

  return (
    <main className="min-h-screen bg-background px-3 py-3 sm:px-6 sm:py-8">
      <div className="mx-auto flex max-w-xl flex-col gap-4 sm:gap-6">
        {/* Progress header */}
        <header className="panel relative overflow-hidden border-accent bg-secondary text-secondary-foreground">
          <div className="halftone absolute inset-0 opacity-[0.08]" aria-hidden />
          <div className="relative px-4 py-4 sm:px-6 sm:py-6">
            <div className="flex items-center gap-3 sm:gap-4">
              <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-accent text-accent-foreground sm:h-12 sm:w-12">
                <Crown className="h-5 w-5 fill-current sm:h-6 sm:w-6" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="font-mono text-[9px] font-black uppercase tracking-[0.16em] opacity-70 sm:text-[10px] sm:tracking-[0.18em]">
                  VIP Pass Progress
                </p>
                <p className="font-display text-xl leading-none sm:text-3xl">
                  <span className="text-accent">{solvedCount}</span>
                  <span className="opacity-50">/{total}</span> <span>SOLVED</span>
                </p>
              </div>
              <span className="shrink-0 rounded-full bg-accent px-3 py-1 font-mono text-[10px] font-black text-accent-foreground sm:px-3.5 sm:py-1.5 sm:text-xs">
                {pct}%
              </span>
            </div>
            <div className="mt-4 flex gap-1.5 sm:mt-5">
              {shorteners.map((s) => (
                <div
                  key={s.id}
                  className={
                    "h-1.5 flex-1 rounded-full sm:h-2 " +
                    (s.already_solved
                      ? "bg-accent"
                      : s.reported
                        ? "stripes bg-secondary-foreground/15"
                        : "bg-secondary-foreground/15")
                  }
                />
              ))}
            </div>
            <p className="mt-3 text-[11px] leading-relaxed opacity-90 sm:mt-4 sm:text-sm">
              Every link below gives you{" "}
              <span className="font-black text-accent">this file, right away</span>. Solve{" "}
              <span className="font-black">{remaining} more</span> total (any files) to skip the
              shortener step for <span className="font-black">24 hours</span>.
            </p>
          </div>
        </header>

        {/* The one instruction on this page */}
        <div className="text-center">
          <h1 className="font-display text-2xl sm:text-3xl">Tap a link to get your file</h1>
          <p className="mt-1 text-xs text-muted-foreground sm:text-sm">
            Each one leads to a short ad page, then straight back to your download.
          </p>
        </div>

        {/* Shortener buttons */}
        <div className="grid grid-cols-2 gap-3 sm:gap-4">
          {shorteners.map((s, i) => (
            <ShortenerCard
              key={s.id}
              shortener={s}
              tintIndex={i}
              isPending={startUnlock.isPending && startUnlock.variables === s.id}
              disabledByOther={startUnlock.isPending && startUnlock.variables !== s.id}
              onUnlock={() => unlock(s)}
              onInfo={() => setInfoTarget(s)}
              onReport={() => openReport(s)}
            />
          ))}
        </div>

        {startUnlock.isError && (
          <p className="text-center text-xs font-bold text-destructive">
            {startUnlock.error instanceof ApiError
              ? startUnlock.error.message
              : "Couldn't start that link, try another one."}
          </p>
        )}

        {!anyAvailable && (
          <p className="panel p-4 text-center text-sm text-muted-foreground">
            All links are solved or reported. Check back in 24 hours, or report an issue above.
          </p>
        )}

        <p className="text-center font-mono text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
          Free · No signup
        </p>
      </div>

      {/* Info modal: hint + optional tutorial video, per shortener */}
      {infoTarget && (
        <div
          role="dialog"
          aria-modal="true"
          onClick={() => setInfoTarget(null)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-sm overflow-hidden border-[3px] border-border bg-background shadow-[6px_6px_0_0_var(--color-border)]"
          >
            <div className="flex items-center gap-2 border-b-[3px] border-border bg-secondary px-3 py-2 text-secondary-foreground">
              <HelpCircle className="h-4 w-4" />
              <span className="label-cap truncate">How to solve {infoTarget.name}</span>
              <button
                type="button"
                onClick={() => setInfoTarget(null)}
                aria-label="Close"
                className="ml-auto grid h-7 w-7 place-items-center border-2 border-secondary-foreground bg-primary text-primary-foreground hover:brightness-110"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
            {infoTarget.message && (
              <p className="p-4 text-sm text-foreground">{infoTarget.message}</p>
            )}
            {infoTarget.how_to_video_url && (
              <iframe
                src={infoTarget.how_to_video_url}
                title={`How to solve ${infoTarget.name}`}
                allowFullScreen
                className="aspect-video w-full bg-black"
              />
            )}
            {!infoTarget.message && !infoTarget.how_to_video_url && (
              <p className="p-4 text-sm text-muted-foreground">
                No tips for this one yet — it should be straightforward.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Report modal */}
      {reportTarget && (
        <div
          role="dialog"
          aria-modal="true"
          onClick={() => setReportTarget(null)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-sm overflow-hidden rounded-lg border border-border bg-card text-card-foreground shadow-xl"
          >
            <div className="flex items-center gap-2 bg-secondary px-4 py-3 text-secondary-foreground">
              <AlertTriangle className="h-4 w-4 text-accent" />
              <span className="label-cap">Report broken link</span>
              <button
                type="button"
                onClick={() => setReportTarget(null)}
                aria-label="Close"
                className="ml-auto grid h-7 w-7 place-items-center rounded-full text-secondary-foreground/80 transition hover:bg-white/10 hover:text-secondary-foreground"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
            <div className="p-4">
              <p className="font-display text-xl leading-none sm:text-2xl">
                What's wrong with {reportTarget.name}?
              </p>
              <div className="mt-4 flex flex-col gap-2">
                {[
                  { id: "Captcha broken", label: "Captcha broken" },
                  { id: "Infinite loop", label: "Infinite loop" },
                  { id: "Inappropriate ads", label: "Inappropriate ads" },
                  { id: "Not working", label: "Doesn't work at all" },
                ].map((opt) => (
                  <label
                    key={opt.id}
                    className={
                      "flex cursor-pointer items-center gap-3 rounded-md border px-3 py-2 text-sm font-bold transition " +
                      (reportReason === opt.id
                        ? "border-primary bg-primary/10 text-foreground"
                        : "border-border bg-transparent text-foreground hover:bg-muted")
                    }
                  >
                    <input
                      type="radio"
                      name="report-reason"
                      value={opt.id}
                      checked={reportReason === opt.id}
                      onChange={() => setReportReason(opt.id)}
                      className="h-4 w-4 accent-primary"
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
              <label className="mt-3 block">
                <span className="label-cap text-muted-foreground">Describe it (optional)</span>
                <Textarea
                  value={reportDetails}
                  onChange={(e) => setReportDetails(e.target.value)}
                  placeholder="What happened when you tried it?"
                  maxLength={300}
                  className="mt-1.5"
                />
              </label>
              <div className="mt-5 flex items-center gap-3">
                <button
                  type="button"
                  onClick={submitReport}
                  disabled={reportShortener.isPending}
                  className="btn-base flex-1 justify-center bg-primary text-primary-foreground disabled:opacity-60"
                >
                  {reportShortener.isPending ? "Submitting…" : "Submit"}
                </button>
                <button
                  type="button"
                  onClick={() => setReportTarget(null)}
                  className="font-mono text-xs font-black uppercase tracking-widest opacity-80 hover:underline"
                >
                  Cancel
                </button>
              </div>
              {reportShortener.isError && (
                <p className="mt-2 text-xs font-bold text-destructive">
                  {reportShortener.error instanceof ApiError
                    ? reportShortener.error.message
                    : "Couldn't submit the report."}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

// Rotating icon-badge tints for available cards - purely decorative variety,
// not tied to any backend data (unlike DownloadCard's server colors, which are
// admin-configured and semantic).
const BADGE_TINTS = [
  "bg-primary text-primary-foreground",
  "bg-accent text-accent-foreground",
  "bg-[#2563eb] text-white",
  "bg-[#16a34a] text-white",
];

function ShortenerCard({
  shortener,
  tintIndex,
  isPending,
  disabledByOther,
  onUnlock,
  onInfo,
  onReport,
}: {
  shortener: ShortenerOption;
  tintIndex: number;
  isPending: boolean;
  disabledByOther: boolean;
  onUnlock: () => void;
  onInfo: () => void;
  onReport: () => void;
}) {
  const done = shortener.already_solved;
  const reported = shortener.reported;
  const disabled = done || reported || disabledByOther;
  const hasInfo = Boolean(shortener.message || shortener.how_to_video_url);
  const tint = BADGE_TINTS[tintIndex % BADGE_TINTS.length];

  return (
    <div
      className={
        "relative overflow-hidden rounded-md border-2 border-border shadow-[4px_4px_0_0_var(--color-border)] transition " +
        (done || reported ? "bg-muted" : "bg-card hover:-translate-y-0.5")
      }
    >
      <button
        type="button"
        disabled={disabled}
        onClick={onUnlock}
        className="flex w-full flex-col items-center gap-1.5 px-3 pb-3.5 pt-4 text-center transition disabled:cursor-not-allowed sm:pb-4 sm:pt-5"
      >
        <span
          className={
            "grid h-10 w-10 shrink-0 place-items-center overflow-hidden rounded-full border-2 border-border sm:h-12 sm:w-12 " +
            (shortener.logo_url
              ? "bg-white"
              : done || reported
                ? "bg-muted text-muted-foreground"
                : tint)
          }
        >
          {isPending ? (
            <Loader2 className="h-4 w-4 animate-spin sm:h-5 sm:w-5" />
          ) : shortener.logo_url ? (
            <img
              src={shortener.logo_url}
              alt=""
              className={
                "h-6 w-6 object-contain sm:h-7 sm:w-7 " + (done || reported ? "grayscale" : "")
              }
            />
          ) : done ? (
            <Check className="h-4 w-4 sm:h-5 sm:w-5" />
          ) : reported ? (
            <AlertTriangle className="h-4 w-4 sm:h-5 sm:w-5" />
          ) : (
            <Zap className="h-4 w-4 fill-current sm:h-5 sm:w-5" />
          )}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="font-display text-lg leading-none sm:text-xl">{shortener.name}</span>
          {done && <Check className="-translate-y-px h-4 w-4 shrink-0 text-[#16a34a]" />}
          {reported && <AlertTriangle className="-translate-y-px h-4 w-4 shrink-0 text-primary" />}
        </span>
        <span
          className={
            "label-cap " +
            (done ? "text-[#16a34a]" : reported ? "text-primary" : "text-muted-foreground")
          }
        >
          {isPending
            ? "Redirecting…"
            : done
              ? "Already solved"
              : reported
                ? "Reported broken"
                : "Tap to unlock"}
        </span>
      </button>

      {!done && !reported && (
        <div className="absolute right-2 top-2 flex gap-2.5">
          {hasInfo && (
            <button
              type="button"
              onClick={onInfo}
              aria-label={`How to solve ${shortener.name}`}
              className="text-[#2563eb] transition hover:opacity-70"
            >
              <HelpCircle className="h-5 w-5" />
            </button>
          )}
          <button
            type="button"
            onClick={onReport}
            aria-label={`Report ${shortener.name} as broken`}
            className="text-primary transition hover:opacity-70"
          >
            <AlertTriangle className="h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  );
}
