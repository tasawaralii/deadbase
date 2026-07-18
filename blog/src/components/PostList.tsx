import Image from "next/image";
import Link from "next/link";
import { Clock, MessageSquare, SearchX, User } from "lucide-react";
import type { PostSummary } from "@/lib/types";
import { timeAgo } from "@/lib/format";

function buildPageWindow(current: number, total: number): (number | "…")[] {
  if (total <= 1) return [1];
  const pages = new Set([1, total, current - 1, current, current + 1]);
  const sorted = [...pages].filter((n) => n >= 1 && n <= total).sort((a, b) => a - b);

  const result: (number | "…")[] = [];
  let prev = 0;
  for (const n of sorted) {
    if (prev && n - prev > 1) result.push("…");
    result.push(n);
    prev = n;
  }
  return result;
}

function pageHref(basePath: string, query: Record<string, string>, page: number): string {
  const params = new URLSearchParams(query);
  if (page > 1) params.set("page", String(page));
  else params.delete("page");
  const qs = params.toString();
  return qs ? `${basePath}?${qs}` : basePath;
}

export function PostList({
  posts,
  page,
  limit,
  count,
  basePath = "/",
  query = {},
  emptyMessage = "Try a different search, or check back later for new releases.",
}: {
  posts: PostSummary[];
  page: number;
  limit: number;
  count: number;
  basePath?: string;
  query?: Record<string, string>;
  emptyMessage?: string;
}) {
  const totalPages = Math.max(1, Math.ceil(count / limit));

  if (posts.length === 0) {
    return (
      <div className="py-20 text-center">
        <SearchX className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
        <h3 className="font-display font-semibold text-xl mb-2">No posts found</h3>
        <p className="text-sm text-muted-foreground max-w-sm mx-auto">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <>
      <ul>
        {posts.map((p) => (
          <li key={p.slug} className="py-6 flex flex-col sm:flex-row gap-5">
            <Link
              href={`/posts/${p.slug}`}
              className="shrink-0 block sm:w-64 sm:self-center aspect-video overflow-hidden rounded-sm bg-muted"
            >
              <Image
                src={p.backdrop_img.mid || "/poster-1.jpg"}
                alt=""
                width={1024}
                height={768}
                className="w-full h-full object-cover"
              />
            </Link>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap gap-x-2 gap-y-1 text-sm font-semibold mb-1.5">
                {p.tags.map((t, i) => (
                  <span key={t.slug}>
                    <Link href={`/category/${t.slug}`} className="text-accent hover:underline">
                      {t.name}
                    </Link>
                    {i < p.tags.length - 1 && <span className="text-muted-foreground ml-2">·</span>}
                  </span>
                ))}
              </div>
              <h2 className="font-display font-semibold text-2xl sm:text-3xl leading-tight text-foreground hover:text-accent transition-colors">
                <Link href={`/posts/${p.slug}`} className="flex gap-2">
                  <span>{p.title}</span>
                </Link>
              </h2>
              <div className="flex flex-wrap items-center gap-4 mt-4 text-xs font-medium text-muted-foreground">
                <span className="inline-flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {timeAgo(p.last_updated)}
                </span>
                <span className="inline-flex items-center gap-1">
                  <MessageSquare className="w-3 h-3" /> {p.comment_count} Comments
                </span>
                <span className="inline-flex items-center gap-1">
                  <User className="w-3 h-3" /> {p.author?.display_name ?? "Admin"}
                </span>
              </div>
            </div>
          </li>
        ))}
      </ul>

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-8 flex-wrap gap-3">
          {page > 1 && (
            <Link
              href={pageHref(basePath, query, page - 1)}
              className="bg-accent text-accent-foreground font-semibold text-sm px-6 h-9 grid place-items-center rounded-sm hover:opacity-90"
            >
              ‹ PREV
            </Link>
          )}
          <div className="flex items-center gap-1">
            {buildPageWindow(page, totalPages).map((n, i) =>
              n === "…" ? (
                <span key={`ellipsis-${i}`} className="px-2 text-muted-foreground">
                  …
                </span>
              ) : (
                <Link
                  key={n}
                  href={pageHref(basePath, query, n)}
                  className={`grid place-items-center w-9 h-9 text-sm font-semibold rounded-sm ${
                    n === page
                      ? "bg-accent text-accent-foreground"
                      : "bg-muted text-foreground hover:bg-border"
                  }`}
                >
                  {n}
                </Link>
              )
            )}
          </div>
          {page < totalPages && (
            <Link
              href={pageHref(basePath, query, page + 1)}
              className="bg-accent text-accent-foreground font-semibold text-sm px-6 h-9 grid place-items-center rounded-sm hover:opacity-90"
            >
              NEXT ›
            </Link>
          )}
        </div>
      )}
    </>
  );
}
