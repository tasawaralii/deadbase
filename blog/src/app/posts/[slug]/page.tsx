import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Clock } from "lucide-react";
import { Layout } from "@/components/Layout";
import { CommentsSection } from "@/components/CommentsSection";
import { ApiError } from "@/lib/api";
import { getPost, getPosts } from "@/lib/posts";
import { buildPostView } from "@/lib/post-view";
import { timeAgo } from "@/lib/format";

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;

  const post = await getPost(slug).catch((err) => {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  });
  const view = buildPostView(post);

  // Comments are fetched client-side in CommentsSection - they change far
  // more often than the post content, so they shouldn't share this page's
  // cache lifetime, and skipping them here keeps the cached HTML smaller.
  const related = (await getPosts({ limit: 5 })).data
    .filter((p) => p.slug !== post.slug)
    .slice(0, 4);

  return (
    <Layout>
      <article>
        <div className="flex flex-wrap gap-x-2 gap-y-1 text-sm font-semibold mb-2">
          {post.tags.map((t, i) => (
            <span key={t.slug}>
              <Link href={`/category/${t.slug}`} className="text-accent hover:underline">
                {t.name}
              </Link>
              {i < post.tags.length - 1 && <span className="text-muted-foreground ml-2">·</span>}
            </span>
          ))}
        </div>
        <h1 className="font-display font-semibold text-2xl sm:text-3xl leading-tight mb-3">
          {post.title}
        </h1>
        <div className="flex items-center gap-1 mb-6 text-xs font-medium text-muted-foreground">
          <Clock className="w-3 h-3" /> {timeAgo(post.last_updated)}
        </div>

        {view.backdropUrl && (
          <Image
            src={view.backdropUrl}
            alt={post.title}
            width={1280}
            height={720}
            className="w-full aspect-video object-cover rounded-md mb-6"
          />
        )}

        {!view.isMovie && view.languageMode && (
          <>
            <p className="text-sm leading-relaxed text-foreground/90 mb-4">
              ✅ Download <b>{post.anime_name}</b> Season {post.season?.season_number} Dubbed by{" "}
              <b>{view.otts.join(",")}</b> {view.languageMode} Audio{" "}
              <b>[{view.languages.join("-")}]</b> Complete All Episodes WEB-DL HD in 480p & 720p & 1080p.
              This season was released on <b>{view.releaseDate}</b>. It is based on{" "}
              <b>{view.genres.join(",")}</b>. This Season has <b>{view.totalEpisodes} Episodes</b>. This
              Series is now available in <strong>Hindi Dubbed at Deadtoons.</strong>
            </p>
            <hr className="mb-6 border-border" />
          </>
        )}


        <ul className="text-sm leading-relaxed mb-6 space-y-1">
          <li>
            Full Name: <strong>{post.anime_name}</strong>
          </li>
          {!view.isMovie && (
            <>
              <li>
                Season: <strong>{post.season?.season_number}</strong>
              </li>
              <li>
                Episodes: <strong>{view.totalEpisodes}</strong>
              </li>
            </>
          )}
          {view.releaseYear && (
            <li>
              Year: <strong>{view.releaseYear}</strong>
            </li>
          )}
          {view.rating && (
            <li>
              Rating: <strong>{view.rating} / 10</strong>
            </li>
          )}
          {view.isMovie && view.ageRating && (
            <li>
              Age Rating: <strong>{view.ageRating}</strong>
            </li>
          )}
          {view.isMovie && view.durationMinutes && (
            <li>
              Duration: <strong>{view.durationMinutes} min</strong>
            </li>
          )}
          {view.genres.length > 0 && (
            <li>
              Genre: <strong>{view.genres.join(", ")}</strong>
            </li>
          )}
          {view.languageMode && (
            <li>
              Language:{" "}
              <strong>
                {view.languageMode} Audio ({view.languages.join("-")})
              </strong>
            </li>
          )}
          {view.releaseDate && (
            <li>
              Release Date: <strong>{view.releaseDate}</strong>
            </li>
          )}
          <li>
            Format: <strong>Mkv</strong>
          </li>
        </ul>

        <h2 className="font-display font-bold text-xl mb-3">Storyline</h2>
        <p className="text-sm leading-relaxed text-foreground/90 mb-4">{view.overview}</p>

        {view.screenshots.length > 0 && (
          <section className="mb-10">
            <h2 className="bg-muted inline-block px-3 py-1.5 font-display font-semibold text-sm border-b-2 border-primary mb-4">
              Screenshots
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2">
              {view.screenshots.map((src, i) => (
                <Image
                  key={src + i}
                  src={src}
                  alt=""
                  width={334}
                  height={188}
                  className="w-full aspect-auto object-cover rounded-sm"
                />
              ))}
            </div>
          </section>
        )}

        <section className="mb-10">
          <h2 className="bg-muted inline-block px-3 py-1.5 font-display font-semibold text-sm border-b-2 border-primary mb-4">
            Download {post.anime_name}
          </h2>

          {view.posterUrl && (
            <Image
              src={view.posterUrl}
              alt={post.anime_name}
              width={200}
              height={300}
              className="w-50 aspect-2/3 object-cover rounded-md mx-auto mb-6"
            />
          )}

          {view.isMovie ? (
            <a
              href={view.movieHref ?? "#"}
              rel="nofollow"
              className="block text-center bg-accent text-accent-foreground font-bold px-6 py-3 uppercase text-sm rounded-sm hover:opacity-90"
            >
              Download
            </a>
          ) : (
            <>
              <ul className="divide-y divide-border">
                {view.episodes.map((e) => (
                  <li key={e.episodeNumber} className="py-4 text-center">
                    <div className="font-semibold text-sm mb-2">
                      Episode {e.episodeNumber}: {e.name}
                      {e.note && <span className="text-accent"> ({e.note})</span>}
                    </div>
                    <a
                      href={e.href}
                      rel="nofollow"
                      className="inline-block bg-accent text-accent-foreground font-bold px-6 py-2 uppercase text-xs rounded-sm hover:opacity-90"
                    >
                      Download
                    </a>
                  </li>
                ))}
              </ul>

              {view.skippedEpisodes.length > 0 && (
                <p className="text-center text-xs text-muted-foreground mt-4">
                  {view.skippedEpisodes.length === 1
                    ? `Note: Episode ${view.skippedEpisodes[0]} is not available and will be added when available.`
                    : `Note: Following episodes are skipped and will be added when available: ${view.skippedEpisodes.join(", ")}`}
                </p>
              )}

              {view.packs.length > 0 && (
                <div className="pack-links mt-6 max-w-100 mx-auto bg-muted rounded-md p-4">
                  <h3 className="text-center font-display font-semibold text-sm mb-3">Pack Links</h3>
                  {view.packs.map((p) => (
                    <a
                      key={p.label}
                      href={p.href}
                      rel="nofollow"
                      className="block text-center px-4 py-2 mb-2 last:mb-0 bg-white border border-border rounded text-sm font-medium hover:border-accent hover:text-accent transition-colors"
                    >
                      {p.label}
                    </a>
                  ))}
                </div>
              )}
            </>
          )}
        </section>

        {related.length > 0 && (
          <section className="mb-10">
            <h2 className="bg-muted inline-block px-3 py-1.5 font-display font-semibold text-sm border-b-2 border-primary">
              You may also like
            </h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {related.map((r) => (
                <Link
                  key={r.slug}
                  href={`/posts/${r.slug}`}
                  className="block relative rounded overflow-hidden group max-w-100 mx-auto"
                >
                  <Image
                    src={r.backdrop_img.mid || "/poster-1.jpg"}
                    alt=""
                    width={1280}
                    height={720}
                    className="w-full aspect-video object-cover"
                  />
                  <div className="absolute inset-0 bg-linear-to-t from-black/80 via-black/40 to-transparent" />
                  <div className="absolute inset-0 grid place-items-center p-6 text-center">
                    <h3 className="text-white font-display font-bold text-lg sm:text-xl leading-tight">
                      {r.title}
                    </h3>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        <section className="mb-10 border border-border rounded p-4 flex items-start gap-4">
          <Image
            src={post.author?.avatar_url ?? "/favicon.png"}
            alt={post.author?.display_name ?? "Admin"}
            width={64}
            height={64}
            className="w-16 h-16 rounded-full object-cover shrink-0"
          />
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2 border-b border-border pb-2">
              <h3 className="bg-muted px-3 py-1 text-sm font-display font-semibold">About the author</h3>
              {post.author && (
                <Link
                  href={`/author/${post.author.slug}`}
                  className="bg-accent text-accent-foreground text-xs font-bold px-3 py-1.5 uppercase"
                >
                  View all posts
                </Link>
              )}
            </div>
            <div className="font-display font-bold text-lg">
              {post.author?.display_name ?? "Admin"}
            </div>
            <p className="text-sm text-muted-foreground">Deadtoons isn&apos;t Dead. So don&apos;t worry.</p>
          </div>
        </section>

        <CommentsSection slug={post.slug} />
      </article>
    </Layout>
  );
}
