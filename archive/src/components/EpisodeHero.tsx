import { CalendarDays, Clock, Play, Star } from "lucide-react";
import type { Episode } from "@/data/episode";

type Props = { episode: Episode };

export function EpisodeHero({ episode }: Props) {
  const d = episode.releaseDate ? new Date(episode.releaseDate) : null;
  const formattedDate =
    d && !Number.isNaN(d.getTime())
      ? `${d.getUTCDate().toString().padStart(2, "0")} ${d
          .toLocaleString("en-US", { month: "short", timeZone: "UTC" })
          .toUpperCase()} ${d.getUTCFullYear()}`
      : null;

  // Movies have neither season nor episode number. Packs have a season but
  // span multiple episodes, so there's no single episode number either.
  const hasSeason = episode.seasonNumber !== undefined;
  const hasEpisodeNumber = episode.episodeNumber !== undefined;
  const showWatchAction = (hasEpisodeNumber || !hasSeason) && episode.hasWatchServers;
  const epNum = episode.episodeNumber?.toString().padStart(2, "0");

  return (
    <section className="panel overflow-hidden">
      {/* Top strip — series marquee */}
      <div className="flex items-stretch border-b-2 border-border bg-secondary text-secondary-foreground">
        <div className="flex items-center gap-2 px-3 py-2 sm:px-4">
          <span className="grid h-6 w-6 place-items-center bg-primary text-[10px] font-black text-primary-foreground sm:h-7 sm:w-7">
            ▶
          </span>
          <span className="label-cap">{hasSeason ? episode.animeTitle : "Movie"}</span>
        </div>
        {hasSeason && (
          <div className="ml-auto flex items-center border-l-2 border-border bg-accent px-3 text-accent-foreground">
            <span className="label-cap">S{episode.seasonNumber}</span>
          </div>
        )}
      </div>

      {/* Body: poster (vertical) beside info */}
      <div className="grid grid-cols-[7.5rem_minmax(0,1fr)] sm:grid-cols-[13rem_minmax(0,1fr)]">
        <div className="relative border-r-2 border-border bg-ink">
          <img
            src={episode.poster}
            alt={`${episode.animeTitle} poster`}
            className="aspect-[2/3] h-full w-full object-cover"
          />
          {hasSeason && (
            <span className="absolute left-1.5 top-1.5 border-2 border-border bg-background/90 px-1.5 py-0.5 font-mono text-[9px] font-bold uppercase tracking-widest text-foreground">
              S{episode.seasonNumber}
            </span>
          )}
          {/* Rating stamp — bottom-right, tilted, bleeds off corner. z-10 so
              it paints above the action bar it overlaps into. */}
          <span className="absolute -bottom-2 -right-2 z-10 inline-flex rotate-[-8deg] items-center gap-1 border-2 border-border bg-accent px-2 py-1 font-mono text-xs font-black text-accent-foreground shadow-[3px_3px_0_0_var(--color-border)]">
            <Star className="h-3 w-3 fill-current" />
            {episode.rating.toFixed(1)}
          </span>
        </div>

        <div className="flex min-w-0 flex-col p-3 sm:p-6">
          {hasEpisodeNumber && (
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-xs font-bold text-primary">EP</span>
              <span className="font-display text-4xl leading-none text-primary sm:text-6xl">
                {epNum}
              </span>
            </div>
          )}

          <h1
            className={
              "font-display text-lg leading-tight sm:text-4xl " +
              (hasEpisodeNumber ? "mt-1 sm:mt-2" : "")
            }
          >
            {episode.title}
          </h1>

          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[10px] text-muted-foreground sm:mt-3 sm:text-xs">
            {formattedDate && (
              <>
                <span className="inline-flex items-center gap-1">
                  <CalendarDays className="h-3 w-3" />
                  {formattedDate}
                </span>
                <span aria-hidden>·</span>
              </>
            )}
            <span className="inline-flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {episode.duration.toUpperCase()}
            </span>
          </div>

          <p className="mt-3 hidden text-sm leading-relaxed text-foreground/80 sm:block sm:mt-4">
            {episode.description}
          </p>
        </div>
      </div>

      {/* Mobile-only description below (keeps grid tidy on small screens) */}
      <p className="border-t-2 border-border p-3 text-sm leading-relaxed text-foreground/80 sm:hidden">
        {episode.description}
      </p>

      {/* Action bar */}
      <div className="halftone grid grid-cols-1 items-stretch border-t-2 border-border bg-muted/40 sm:grid-cols-[minmax(0,1fr)_auto]">
        {showWatchAction && (
          <button className="group relative flex items-center justify-center gap-3 bg-primary px-4 py-4 text-primary-foreground transition hover:brightness-110 sm:justify-start sm:px-6 sm:py-5">
            <span className="grid h-9 w-9 shrink-0 place-items-center border-2 border-primary-foreground/90 bg-primary-foreground/10 sm:h-11 sm:w-11">
              <Play className="h-4 w-4 fill-current sm:h-5 sm:w-5" />
            </span>
            <span className="flex flex-col items-start leading-none">
              <span className="font-mono text-[10px] font-bold uppercase tracking-widest opacity-80">
                Stream now
              </span>
              <span className="font-display text-xl sm:text-2xl">Watch Online</span>
            </span>
            <span className="ml-auto hidden font-mono text-[10px] font-bold uppercase tracking-widest opacity-80 sm:inline">
              HD · Multi-server →
            </span>
          </button>
        )}
        <a
          href="#downloads"
          className="flex items-center justify-center gap-2 border-border bg-accent px-6 text-accent-foreground transition hover:brightness-105 sm:border-l-2"
        >
          <span className="label-cap">Downloads</span>
          <span className="font-display text-xl">↓</span>
        </a>
      </div>
    </section>
  );
}
