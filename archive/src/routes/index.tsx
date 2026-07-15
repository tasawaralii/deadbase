import { createFileRoute, Link } from "@tanstack/react-router";
import { ExternalLink, Flame } from "lucide-react";
import { Layout } from "@/components/Layout";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Deadtoons — Anime Archive" },
      {
        name: "description",
        content:
          "Deadtoons — download and watch your favorite anime. Check the trending episodes this week.",
      },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <Layout>
      {/* Hero panel — arcade marquee */}
      <section className="panel relative mx-auto max-w-3xl overflow-hidden">
        <div className="halftone absolute inset-0 opacity-[0.06]" aria-hidden />
        <div className="relative flex items-stretch border-b-2 border-border bg-secondary text-secondary-foreground">
          {/* <span className="label-cap px-3 py-2 sm:px-4">// Est. 2024</span> */}
          <span className="ml-auto label-cap border-l-2 border-border bg-primary px-3 py-2 text-primary-foreground">
            ANIME · ARCHIVE
          </span>
        </div>

        <div className="relative p-5 sm:p-10">
          <p className="label-cap text-primary">Deadtoons archive</p>
          <h1 className="mt-2 font-display text-4xl leading-[0.9] sm:text-6xl md:text-7xl">
            Watch. Download.
            <br />
            <span className="text-primary">Enjoy.</span>
          </h1>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-foreground/75 sm:text-base">
            Head over to Deadtoons for the full library of subbed & dubbed episodes,
            multiple qualities, and lightning-fast download mirrors.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <a
              href="https://archive.deadtoons.sbs"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-base bg-primary text-primary-foreground"
            >
              Visit DeadToons <ExternalLink className="h-3.5 w-3.5" />
            </a>
            <Link
              to="/trending"
              className="btn-base bg-card text-foreground"
            >
              <Flame className="h-3.5 w-3.5 text-primary" /> Trending
            </Link>
          </div>
        </div>
      </section>

      {/* Trending call-out — ticket style */}
      <section className="mx-auto mt-5 max-w-3xl">
        <Link
          to="/trending"
          className="ticket group flex items-stretch overflow-hidden transition hover:-translate-x-0.5 hover:-translate-y-0.5"
        >
          <div className="stripes flex w-14 shrink-0 items-center justify-center border-r-2 border-dashed border-border bg-accent sm:w-20">
            <Flame className="h-6 w-6 text-accent-foreground sm:h-8 sm:w-8" />
          </div>
          <div className="min-w-0 flex-1 p-4 sm:p-5">
            <p className="label-cap text-primary">This week</p>
            <h2 className="mt-1 font-display text-xl leading-tight sm:text-3xl">
              7 most-watched episodes
            </h2>
            <p className="mt-1 text-xs text-muted-foreground sm:text-sm">
              Updated every Monday · pulled from the last 7 days.
            </p>
          </div>
          <div className="flex items-center justify-center border-l-2 border-border bg-secondary px-3 text-secondary-foreground transition group-hover:bg-primary group-hover:text-primary-foreground sm:px-5">
            <ExternalLink className="h-4 w-4" />
          </div>
        </Link>
      </section>
    </Layout>
  );
}
