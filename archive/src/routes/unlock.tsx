import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { z } from "zod";
import {
  AlertTriangle,
  ArrowRight,
  Check,
  Crown,
  Download,
  HelpCircle,
  Radio,
  X,
  Zap,
} from "lucide-react";
import { useReportShortener, useStartUnlock, useUnlockStatus } from "@/hooks/use-api";
import type { ShortenerOption } from "@/lib/types";
import { ApiError } from "@/lib/api";

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
        content: "Solve shortener links to unlock ad-free downloads for 24h.",
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

  const [selectedShortener, setSelectedShortener] = useState<number | null>(null);
  const [isTutorialOpen, setIsTutorialOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [reportReason, setReportReason] = useState("Not working");

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
  const selected = shorteners.find((s) => s.id === selectedShortener) ?? null;
  const selectedName = selected?.name ?? "any link";
  const pct = total > 0 ? Math.round((solvedCount / total) * 100) : 0;

  const submitReport = () => {
    if (!selected) return;
    reportShortener.mutate(
      { shortener_id: selected.id, reason: reportReason },
      {
        onSuccess: () => {
          setSelectedShortener(null);
          setIsReportOpen(false);
        },
      },
    );
  };

  const solveAndUnlock = () => {
    if (!selectedShortener) return;
    startUnlock.mutate(selectedShortener, {
      onSuccess: (data) => {
        window.location.href = data.redirect_url;
      },
    });
  };

  return (
    <main className="min-h-screen bg-background px-3 py-3 sm:px-6 sm:py-8">
      <div className="mx-auto flex max-w-xl flex-col gap-3 sm:gap-5">
        {/* Progress header */}
        <header className="panel relative overflow-hidden border-[3px] bg-secondary text-secondary-foreground">
          <div className="halftone absolute inset-0 opacity-[0.10]" aria-hidden />
          <div className="relative px-3 py-3 sm:px-5 sm:py-5">
            <div className="flex items-center gap-2.5 sm:gap-3">
              <span className="grid h-9 w-9 shrink-0 place-items-center border-2 border-accent bg-accent text-accent-foreground sm:h-11 sm:w-11">
                <Crown className="h-4 w-4 fill-current sm:h-6 sm:w-6" />
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
              <span className="shrink-0 border-2 border-accent bg-accent px-1.5 py-0.5 font-mono text-[10px] font-black text-accent-foreground sm:px-2 sm:py-1 sm:text-xs">
                {pct}%
              </span>
            </div>
            <div className="mt-3 flex gap-1.5 sm:mt-4">
              {shorteners.map((s) => (
                <div
                  key={s.id}
                  className={
                    "h-2 flex-1 border-2 border-secondary-foreground/70 sm:h-2.5 " +
                    (s.already_solved ? "bg-accent" : s.reported ? "stripes" : "bg-transparent")
                  }
                />
              ))}
            </div>
            <p className="mt-2.5 text-[11px] leading-snug opacity-90 sm:mt-3 sm:text-sm">
              Solve{" "}
              <span className="font-black text-accent">
                {Math.max(total - solvedCount, 0)} more link{total - solvedCount === 1 ? "" : "s"}
              </span>{" "}
              below → get ad-free downloads for <span className="font-black">24 hours</span>.
            </p>
          </div>
        </header>

        {/* Step 1: shortener grid */}
        <section className="flex flex-col gap-2">
          <div className="flex items-baseline justify-between gap-2">
            <h2 className="label-cap flex items-center gap-2 text-foreground">
              <span className="grid h-5 w-5 place-items-center border-2 border-border bg-primary font-mono text-[10px] font-black text-primary-foreground">
                1
              </span>
              Pick any one
            </h2>
            <span className="font-mono text-[10px] font-black uppercase tracking-widest text-muted-foreground">
              Tap to select
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:gap-3">
            {shorteners.map((s) => (
              <ShortenerCard
                key={s.id}
                shortener={s}
                isSelected={selectedShortener === s.id}
                onSelect={() => setSelectedShortener(s.id)}
              />
            ))}
          </div>
        </section>

        {/* Step 2: tip + tutorial */}
        <section className="flex flex-col gap-2">
          <h2 className="label-cap flex items-center gap-2 text-foreground">
            <span className="grid h-5 w-5 place-items-center border-2 border-border bg-accent font-mono text-[10px] font-black text-accent-foreground">
              2
            </span>
            Stuck? Watch the guide
          </h2>

          <div className="panel overflow-hidden border-[3px] bg-accent text-accent-foreground">
            <div className="flex items-stretch gap-0">
              <div
                className={`flex min-w-0 flex-1 flex-col justify-center gap-0.5 px-3 py-3 sm:px-4 sm:py-4 ${
                  selected ? "items-start" : "items-center text-center py-4 sm:py-6"
                }`}
              >
                <p className="inline-flex items-center gap-1.5 font-mono text-[9px] font-black uppercase tracking-widest opacity-70 sm:text-[10px]">
                  <HelpCircle className="h-3 w-3 sm:h-3.5 sm:w-3.5" />
                  {selected ? "How to skip" : "Tutorial"}
                </p>

                <p className="mt-0.5 font-display text-base leading-none uppercase font-black sm:text-xl">
                  {selected ? selectedName : "Pick a link first"}
                </p>

                {selected?.message && (
                  <p className="mt-1 text-xs opacity-90 sm:text-sm">{selected.message}</p>
                )}

                {selected?.how_to_video_url && (
                  <button
                    type="button"
                    onClick={() => setIsTutorialOpen(true)}
                    className="mt-1.5 inline-flex w-fit items-center gap-1 border-b-2 border-current pb-0.5 font-mono text-[10px] font-black uppercase tracking-widest hover:opacity-70 transition-opacity sm:text-[11px]"
                  >
                    Play tutorial <ArrowRight className="h-3 w-3" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Step 3: unlock button */}
        <section className="flex flex-col gap-2">
          <h2 className="label-cap flex items-center gap-2 text-foreground">
            <span className="grid h-5 w-5 place-items-center border-2 border-border bg-primary font-mono text-[10px] font-black text-primary-foreground">
              3
            </span>
            Unlock downloads
          </h2>
          <button
            type="button"
            disabled={!selectedShortener || startUnlock.isPending}
            onClick={solveAndUnlock}
            className="btn-base w-full justify-center bg-primary py-3.5 text-sm text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50 sm:py-4 sm:text-lg"
          >
            <Zap className="h-4 w-4 fill-current sm:h-5 sm:w-5" />
            {startUnlock.isPending
              ? "Redirecting…"
              : selectedShortener
                ? `Solve ${selectedName} & Unlock`
                : "Pick a link above first"}
          </button>
          {startUnlock.isError && (
            <p className="text-center text-xs font-bold text-destructive">
              {startUnlock.error instanceof ApiError
                ? startUnlock.error.message
                : "Couldn't start that shortener, try another."}
            </p>
          )}
          <p className="text-center font-mono text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
            Free · No signup · 24h pass
          </p>
        </section>

        {/* Footer report action */}
        <button
          type="button"
          onClick={() => setIsReportOpen(true)}
          disabled={!selectedShortener}
          className="inline-flex items-center justify-center gap-2 border-2 border-dashed border-border bg-muted px-3 py-2 font-mono text-[10px] font-black uppercase tracking-widest text-foreground transition hover:bg-muted/70 disabled:cursor-not-allowed disabled:opacity-50 sm:text-[11px] sm:py-2.5"
        >
          <AlertTriangle className="h-3.5 w-3.5" />
          {selectedShortener ? `Report ${selectedName} as broken` : "Pick a link to report it"}
        </button>
      </div>

      {/* Tutorial modal */}
      {isTutorialOpen && selected?.how_to_video_url && (
        <div
          role="dialog"
          aria-modal="true"
          onClick={() => setIsTutorialOpen(false)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="flex aspect-video h-full max-h-[80vh] w-auto max-w-full flex-col border-[3px] border-border bg-background shadow-[6px_6px_0_0_var(--color-border)]"
          >
            <div className="flex items-center gap-2 border-b-[3px] border-border bg-secondary px-3 py-2 text-secondary-foreground">
              <span className="label-cap truncate">How to solve {selectedName}</span>
              <button
                type="button"
                onClick={() => setIsTutorialOpen(false)}
                aria-label="Close"
                className="ml-auto grid h-8 w-8 place-items-center border-2 border-secondary-foreground bg-primary text-primary-foreground hover:brightness-110"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <iframe
              src={selected.how_to_video_url}
              title={`How to solve ${selectedName}`}
              allowFullScreen
              className="flex-1 bg-black"
            />
          </div>
        </div>
      )}

      {/* Report modal */}
      {isReportOpen && (
        <div
          role="dialog"
          aria-modal="true"
          onClick={() => setIsReportOpen(false)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-sm border-[3px] border-border bg-accent text-accent-foreground shadow-[6px_6px_0_0_var(--color-border)]"
          >
            <div className="flex items-center gap-2 border-b-[3px] border-border bg-secondary px-3 py-2 text-secondary-foreground">
              <AlertTriangle className="h-4 w-4 text-accent" />
              <span className="label-cap">Report broken link</span>
              <button
                type="button"
                onClick={() => setIsReportOpen(false)}
                aria-label="Close"
                className="ml-auto grid h-7 w-7 place-items-center border-2 border-secondary-foreground bg-transparent text-secondary-foreground hover:bg-white/10"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
            <div className="p-4">
              <p className="font-display text-xl leading-none sm:text-2xl">
                What's wrong with {selectedName}?
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
                      "flex cursor-pointer items-center gap-3 border-2 border-border bg-background/90 px-3 py-2 text-sm font-bold text-foreground transition " +
                      (reportReason === opt.id ? "shadow-[3px_3px_0_0_var(--color-border)]" : "")
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
                  onClick={() => setIsReportOpen(false)}
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

function ShortenerCard({
  shortener,
  isSelected,
  onSelect,
}: {
  shortener: ShortenerOption;
  isSelected: boolean;
  onSelect: () => void;
}) {
  const disabled = shortener.already_solved || shortener.reported;
  const base =
    "relative flex min-h-[60px] flex-col items-start justify-center gap-1 border-2 border-border px-2.5 py-2 text-left transition sm:min-h-[76px] sm:px-3 sm:py-2.5";
  const state = shortener.already_solved
    ? "bg-muted text-muted-foreground cursor-not-allowed opacity-70"
    : shortener.reported
      ? "bg-muted text-muted-foreground cursor-not-allowed opacity-60"
      : isSelected
        ? "bg-card text-foreground border-primary shadow-[4px_4px_0_0_var(--color-primary)] -translate-x-[1px] -translate-y-[1px]"
        : "bg-card text-foreground hover:-translate-y-[1px] shadow-[3px_3px_0_0_var(--color-border)]";

  return (
    <button type="button" disabled={disabled} onClick={onSelect} className={`${base} ${state}`}>
      <span className="font-display text-base leading-none sm:text-2xl">{shortener.name}</span>
      {shortener.already_solved && (
        <span className="absolute right-1 top-1 inline-flex items-center gap-1 border-2 border-border bg-[#bbf7d0] px-1 py-0.5 font-mono text-[8px] font-black uppercase tracking-widest text-foreground sm:right-1.5 sm:top-1.5 sm:px-1.5 sm:text-[9px]">
          <Check className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
          Done
        </span>
      )}
      {shortener.reported && (
        <span className="absolute right-1 top-1 inline-flex items-center gap-1 border-2 border-border bg-primary px-1 py-0.5 font-mono text-[8px] font-black uppercase tracking-widest text-primary-foreground sm:right-1.5 sm:top-1.5 sm:px-1.5 sm:text-[9px]">
          <AlertTriangle className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
          Reported
        </span>
      )}
      {!disabled && isSelected && (
        <span className="absolute right-1 top-1 inline-flex items-center gap-1 border-2 border-border bg-primary px-1 py-0.5 font-mono text-[8px] font-black uppercase tracking-widest text-primary-foreground sm:right-1.5 sm:top-1.5 sm:px-1.5 sm:text-[9px]">
          <Radio className="h-2.5 w-2.5 fill-current sm:h-3 sm:w-3" />
          Picked
        </span>
      )}
    </button>
  );
}
