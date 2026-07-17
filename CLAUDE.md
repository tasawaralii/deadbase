# deadbase

FastAPI/SQLModel/Postgres backend (cloned from tiangolo's full-stack-fastapi-template)
for an anime streaming/download aggregator — a family of sites: **deadtoons**
(download archive + blog) and **deadstream** (future streaming site). Migrating off a
legacy PHP+MySQL system.

Roadmap order: public API → archive frontend → blog frontend → admin side → Redis
caching → streaming. Streaming is explicitly deferred — do not build it early.

## Repo layout

- `backend/` — FastAPI app. `app/models.py` is the single source of truth for every
  table. `app/api/routes/public/` is the public (unauthenticated) REST API. No admin
  API exists yet.
- `archive/` — the download-archive frontend. TanStack Start (Vite, SSR, file-based
  routing under `src/routes/`), Tailwind v4, shadcn/ui, react-query. Originally
  scaffolded via Lovable.
- Blog frontend (deadtoons blog) — **being built in Next.js**, deliberately a
  different framework than `archive/`. Not TanStack, on purpose (see below).

## Hard rules — do not deviate from these without asking

- **Never add or remove fields to match "cleaner" API design when a legacy PHP
  contract already exists.** The public API's shapes were built to exactly match
  `Helper.php`'s link/response contracts. If a field looks redundant or missing,
  ask before changing it — it's probably intentional parity, not an oversight.
- **No public endpoint ever returns a raw resolved download URL.** Only
  `GET /unlock/{link_server_id}` (after the visitor has done what's required) and
  the `/unlock/callback` redirect resolve real URLs. This is a single-enforcement-
  point security design — don't add a second path that leaks a resolved URL.
- **Never trust a client-supplied redirect target.** Redirects are always resolved
  server-side from an internal reference (`link_server_id`), never from a URL the
  frontend passes in.
- **Unlock-gate reward logic**: solving *any one* shortener immediately unlocks the
  specific file it was solved for — every solve is its own reward. The configured
  `required_solves` count is a *separate bonus tier*: once a visitor has hit that
  count (rolling 24h window), they skip the shortener step entirely for all
  *future* files. Do **not** gate individual file unlocks behind the full count —
  that was tried once this project and explicitly reverted; solving 1 of 4 must
  still hand over that file right away, not require the other 3 first.
- **Blog comments and streaming comments are separate systems, never merge them.**
  `Posts`/`Comments` = download-page feedback (anime/season-scoped, migrated from
  the legacy blog). `StreamComments` = player-page feedback (`content_id`-scoped,
  episode/movie only — packs and browse pages don't get comments). Different
  audiences, different sites, different tables.
- **Anonymous visitor identification is cookie-based** (`VisitorId` in
  `app/api/deps.py`), not tied to authenticated `User` accounts. Public-site
  features (unlock gate, view tracking, comment dedup) key off this cookie, not
  login.

## API shape conventions

- **Summary vs Detail pattern**: list/parent views return lightweight `*Summary`
  schemas with counts only (never grandchildren). Single-resource fetches return
  full `*Detail` + immediate-children summaries. See `app/schemas/*.py`.
- Pack URLs use `{start_ep}-{end_ep}` (readable), not `pack_id` — public endpoints
  intentionally use readable identifiers; opaque IDs are for a future admin side.
- SQLModel gotchas: forward-ref relationships need `Optional["ClassName"]`, not
  `"ClassName" | None` (ruff's UP045 will wrongly revert this — add
  `# noqa: UP045`). Many WHERE/join/order_by/`func.count()` calls need `col()`
  wrapping under strict mypy. Alembic autogenerate does **not** reliably detect new
  PRIMARY KEY additions to existing tables, and re-adds `CREATE TYPE` for enums
  that already exist in the DB (fix: `postgresql.ENUM(..., create_type=False)`) —
  always read the generated migration before applying it.

## Trending / view tracking

Dedup is per `(visitor_id, content_id, day)` — not per anime. A visitor bingeing 5
episodes of one show in a day counts as 5 views rolling up to that anime, not 1;
only *repeat* views of the *same* episode on the *same* day are deduped. Tracking
only fires on player pages (episode/movie), never on browse/info pages. Rollup job
(`backend/scripts/rollup_trending_views.py`) runs in its own `cron` Docker service
(`backend/Dockerfile.cron`), independent of `backend`/`prestart` — it only depends
on `db` being healthy, not on prestart completing, since local dev runs the API via
`fastapi run` on the host rather than the `backend` container.

## Frontend conventions (archive/)

- API calls go through `archive/src/lib/api.ts` (`credentials: "include"` always,
  for the visitor cookie) and typed hooks in `archive/src/hooks/use-api.ts`. TS
  types in `archive/src/lib/types.ts` mirror `backend/app/schemas/*.py` by hand —
  no shared codegen, keep them in sync manually.
- Episode/movie/pack detail pages share **one** view-model (`Episode` type in
  `archive/src/data/episode.ts`) and **one** hero component (`EpisodeHero.tsx`) —
  `seasonNumber`/`episodeNumber`/`contentId`/`hasWatchServers` are all optional
  fields that gate which badges/actions render, rather than three separate
  components. Extend this pattern rather than forking new components when adding
  another content type.
- `hasWatchServers` gates the "Watch Online" action — it's driven by real
  `watch_servers` API data (currently always empty, streaming isn't built), not a
  hardcoded flag. It'll start appearing automatically once streaming exists.
- Design system lives in `archive/src/styles.css` — a restrained "manga cover"
  neo-brutalist theme (warm paper background, cadmium red primary, acid yellow
  accent, small 2-4px radius, hard offset shadows via the `panel`/`ticket`
  utilities). **Use color as an accent, not a fill** — solid wall-to-wall
  saturated-color blocks with thick borders reads as dated "Windows 98" chrome,
  not as this theme. Prefer: neutral card backgrounds with a colored icon
  badge/border/text, not the whole surface painted one color.

## Blog frontend (deadtoons blog) — in progress

Being built fresh in Next.js (App Router), not ported mechanically from the
Lovable/TanStack scaffold — there's no automated cross-framework conversion.
Decision: Next.js over TanStack Start specifically *for the blog*, because a blog
is mostly-static content that benefits from ISR/ISR-style caching and Next's more
mature SEO tooling; `archive/` stays on TanStack Start because it's inherently
dynamic (visitor-cookie personalization, live unlock state) and gets little benefit
from static caching anyway. This is a deliberate framework split, not an oversight
— don't "fix" it by trying to unify them.

The Lovable-generated blog design (React/Tailwind, ~90% matching the original
`deadtoons.sbs` site) is pure static markup with nothing wired up — no data
fetching, no real routing logic. It's a visual/structural reference only, dropped
in `temp_blog/` (or wherever it's placed) — port its Header/Footer/Sidebar/Layout
components and Tailwind theme into the new Next.js app rather than rebuilding them
from scratch from screenshots; porting existing Tailwind/JSX is materially less
work than re-deriving the same visual design from images. The actual post body is
pre-migrated content from the legacy blog DB (see `Posts`/`Comments` in
`models.py`) — it's a content renderer, not a custom-designed component; the real
design work is only Header/Footer/Sidebar/Layout plus the listing and post-detail
page compositions around that migrated content.

## Verification discipline

- For pure Tailwind/class-only frontend changes: `tsc --noEmit` + `eslint` is
  enough. Don't spin up dev servers or curl-test every styling tweak — it's slow
  and the user has explicitly asked not to.
- For anything touching data fetching, hooks, routing, or backend logic: actually
  start the dev server(s) and verify against the real API/DB, not just typecheck.
  This project has caught real bugs this way (a missing `content_id` field, a
  reversed unlock-gate condition, a CORS/env mismatch) that typechecking alone
  would not have caught.
- No Playwright/browser automation tool has been available in this environment so
  far — frontend verification has been via SSR HTML inspection (`curl`) plus
  reasoning about the Tailwind/React code, not actual rendered pixels. If a
  browser tool becomes available, prefer it for anything visual.
- Docker `backend`/`prestart` images go stale often since local dev runs the API
  directly via `fastapi run` on the host, not the `backend` container — don't
  assume `docker compose up` reflects the latest code without rebuilding first.
  The `cron` service is the exception that matters: it only exists in Docker, so
  it does need rebuilding when `app/trending.py`, models, or scripts change.
