import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Check,
  Crown,
  HelpCircle,
  Play,
  Radio,
  X,
  Zap,
} from "lucide-react";

export const Route = createFileRoute("/unlock")({
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

type ShortenerStatus = "pending" | "solved" | "broken";
type Shortener = { id: string; name: string; status: ShortenerStatus; tint: string };

// tint = the flat brutalist swatch color for that shortener card (on-theme, paper palette)
const INITIAL_SHORTENERS: Shortener[] = [
  { id: "shrinkme", name: "ShrinkMe", status: "pending", tint: "bg-[#fde68a]" }, // straw
  { id: "gplinks", name: "GPLinks", status: "solved", tint: "bg-[#bbf7d0]" },   // mint
  { id: "cutty", name: "Cutty", status: "pending", tint: "bg-[#fecaca]" },      // rose
  { id: "exeio", name: "Exe.io", status: "pending", tint: "bg-[#bae6fd]" },     // sky
];

function DownloadUnlockGate() {
  const [shorteners, setShorteners] = useState<Shortener[]>(INITIAL_SHORTENERS);
  const [selectedShortener, setSelectedShortener] = useState<string | null>(null);
  const [isPlayerOpen, setIsPlayerOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [reportReason, setReportReason] = useState("captcha");

  const solvedCount = shorteners.filter((s) => s.status === "solved").length;
  const total = shorteners.length;
  const selected = shorteners.find((s) => s.id === selectedShortener) ?? null;
  const selectedName = selected?.name ?? "any link";
  const pct = Math.round((solvedCount / total) * 100);

  const submitReport = () => {
    if (selected) {
      setShorteners((prev) =>
        prev.map((s) => (s.id === selected.id ? { ...s, status: "broken" } : s)),
      );
      setSelectedShortener(null);
    }
    setIsReportOpen(false);
  };

  const openTutorial = () => {
    if (!selected) return;
    setIsPlayerOpen(true);
  };

  return (
    <main className="min-h-screen bg-background px-3 py-3 sm:px-6 sm:py-8">
      <div className="mx-auto flex max-w-xl flex-col gap-3 sm:gap-5">
        {/* Progress header — on-theme ink slab with acid-yellow accent */}
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
                  <span className="opacity-50">/{total}</span>{" "}
                  <span>SOLVED</span>
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
                    (s.status === "solved"
                      ? "bg-accent"
                      : s.status === "broken"
                        ? "stripes"
                        : "bg-transparent")
                  }
                />
              ))}
            </div>
            <p className="mt-2.5 text-[11px] leading-snug opacity-90 sm:mt-3 sm:text-sm">
              Solve <span className="font-black text-accent">1 link below</span> → get ad-free
              downloads for <span className="font-black">24 hours</span>.
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
            {shorteners.map((s) => {
              const disabled = s.status !== "pending";
              const isSelected = selectedShortener === s.id;
              const base =
                "relative flex min-h-[60px] flex-col items-start justify-center gap-1 border-2 border-border px-2.5 py-2 text-left transition sm:min-h-[76px] sm:px-3 sm:py-2.5";
              const state =
                s.status === "solved"
                  ? "bg-muted text-muted-foreground cursor-not-allowed opacity-70"
                  : s.status === "broken"
                    ? "bg-muted text-muted-foreground cursor-not-allowed opacity-60"
                    : isSelected
                      ? `${s.tint} text-foreground border-primary shadow-[4px_4px_0_0_var(--color-primary)] -translate-x-[1px] -translate-y-[1px]`
                      : `${s.tint} text-foreground hover:-translate-y-[1px] shadow-[3px_3px_0_0_var(--color-border)]`;
              return (
                <button
                  key={s.id}
                  type="button"
                  disabled={disabled}
                  onClick={() => setSelectedShortener(s.id)}
                  className={`${base} ${state}`}
                >
                  <span
                    className={
                      "font-display text-base leading-none sm:text-2xl " +
                      (s.status === "broken" ? "line-through" : "")
                    }
                  >
                    {s.name}
                  </span>
                  {s.status === "solved" && (
                    <span className="absolute right-1 top-1 inline-flex items-center gap-1 border-2 border-border bg-[#bbf7d0] px-1 py-0.5 font-mono text-[8px] font-black uppercase tracking-widest text-foreground sm:right-1.5 sm:top-1.5 sm:px-1.5 sm:text-[9px]">
                      <Check className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                      Done
                    </span>
                  )}
                  {s.status === "broken" && (
                    <span className="absolute right-1 top-1 inline-flex items-center gap-1 border-2 border-border bg-primary px-1 py-0.5 font-mono text-[8px] font-black uppercase tracking-widest text-primary-foreground sm:right-1.5 sm:top-1.5 sm:px-1.5 sm:text-[9px]">
                      <AlertTriangle className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                      Broken
                    </span>
                  )}
                  {s.status === "pending" && isSelected && (
                    <span className="absolute right-1 top-1 inline-flex items-center gap-1 border-2 border-border bg-primary px-1 py-0.5 font-mono text-[8px] font-black uppercase tracking-widest text-primary-foreground sm:right-1.5 sm:top-1.5 sm:px-1.5 sm:text-[9px]">
                      <Radio className="h-2.5 w-2.5 fill-current sm:h-3 sm:w-3" />
                      Picked
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </section>

        {/* Step 2: compact video tutorial — text left, thumb right */}
        <section className="flex flex-col gap-2">
          <h2 className="label-cap flex items-center gap-2 text-foreground">
            <span className="grid h-5 w-5 place-items-center border-2 border-border bg-accent font-mono text-[10px] font-black text-accent-foreground">
              2
            </span>
            Stuck? Watch 30s guide
          </h2>

          <div className="panel overflow-hidden border-[3px] bg-accent text-accent-foreground">
            <div className="flex items-stretch gap-0">
              {/* TEXT */}
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

                {selected && (
                  <button
                    type="button"
                    onClick={openTutorial}
                    className="mt-1.5 inline-flex w-fit items-center gap-1 border-b-2 border-current pb-0.5 font-mono text-[10px] font-black uppercase tracking-widest hover:opacity-70 transition-opacity sm:text-[11px]"
                  >
                    Play tutorial <ArrowRight className="h-3 w-3" />
                  </button>
                )}
              </div>

              {/* THUMB */}
              {selected && (
                <button
                  type="button"
                  onClick={openTutorial}
                  aria-label="Play tutorial video"
                  className="group relative aspect-video w-[38%] shrink-0 border-l-[3px] border-border bg-secondary sm:w-[46%]"
                >
                  <div className="halftone absolute inset-0 opacity-25" aria-hidden />
                  <span className="absolute inset-0 grid place-items-center">
                    <span className="grid h-9 w-9 place-items-center rounded-full border-[3px] border-accent bg-accent/20 text-accent transition group-hover:scale-110 sm:h-12 sm:w-12">
                      <Play className="h-4 w-4 fill-current sm:h-5 sm:w-5" />
                    </span>
                  </span>
                </button>
              )}
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
            disabled={!selectedShortener}
            className="btn-base w-full justify-center bg-primary py-3.5 text-sm text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50 sm:py-4 sm:text-lg"
          >
            <Zap className="h-4 w-4 fill-current sm:h-5 sm:w-5" />
            {selectedShortener ? `Solve ${selectedName} & Unlock` : "Pick a link above first"}
          </button>
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

      {/* Video player modal */}
      {isPlayerOpen && (
        <div
          role="dialog"
          aria-modal="true"
          onClick={() => setIsPlayerOpen(false)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="flex aspect-[9/16] h-full max-h-[92vh] w-auto max-w-full flex-col border-[3px] border-border bg-background shadow-[6px_6px_0_0_var(--color-border)]"
          >
            <div className="flex items-center gap-2 border-b-[3px] border-border bg-secondary px-3 py-2 text-secondary-foreground">
              <span className="label-cap truncate">Bypassing {selectedName}</span>
              <button
                type="button"
                onClick={() => setIsPlayerOpen(false)}
                aria-label="Close"
                className="ml-auto grid h-8 w-8 place-items-center border-2 border-secondary-foreground bg-primary text-primary-foreground hover:brightness-110"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="relative flex-1 bg-secondary">
              <span className="absolute inset-0 grid place-items-center text-accent">
                <span className="grid h-20 w-20 place-items-center rounded-full border-4 border-accent bg-accent/10">
                  <Play className="h-10 w-10 fill-current" />
                </span>
              </span>
              <span className="absolute bottom-3 left-3 border-2 border-accent bg-secondary px-1.5 py-0.5 font-mono text-[10px] font-black uppercase tracking-widest text-accent">
                LIVE · Tutorial
              </span>
            </div>
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
                  { id: "captcha", label: "Captcha broken" },
                  { id: "loop", label: "Infinite loop" },
                  { id: "ads", label: "Inappropriate ads" },
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
                  className="btn-base flex-1 justify-center bg-primary text-primary-foreground"
                >
                  Submit
                </button>
                <button
                  type="button"
                  onClick={() => setIsReportOpen(false)}
                  className="font-mono text-xs font-black uppercase tracking-widest opacity-80 hover:underline"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
