import type { Metadata } from "next";
import { Search } from "lucide-react";
import { Layout } from "@/components/Layout";
import { PageBanner } from "@/components/PageBanner";
import { PostList } from "@/components/PostList";
import { getPosts } from "@/lib/posts";

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}): Promise<Metadata> {
  const { q } = await searchParams;
  return {
    title: q ? `Search results for "${q}"` : "Search",
    // Internal search-result pages are thin/duplicate content and shouldn't
    // compete with real post pages in search rankings.
    robots: { index: false, follow: true },
  };
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; page?: string }>;
}) {
  const { q = "", page } = await searchParams;
  const currentPage = Number(page) > 0 ? Number(page) : 1;
  const { data, limit, count } = await getPosts({ q, page: currentPage });

  return (
    <Layout>
      <PageBanner label={`Search Results for "${q}"`} />
      <form action="/search" className="bg-muted rounded p-4 mb-6 flex items-center gap-2">
        <input
          type="search"
          name="q"
          defaultValue={q}
          placeholder="Search..."
          className="flex-1 h-12 px-4 border border-border rounded text-foreground bg-white outline-none focus:border-primary"
        />
        <button
          type="submit"
          className="h-12 w-12 shrink-0 grid place-items-center bg-accent text-accent-foreground rounded"
          aria-label="Submit search"
        >
          <Search className="w-5 h-5" />
        </button>
      </form>
      <PostList
        posts={data}
        page={currentPage}
        limit={limit}
        count={count}
        basePath="/search"
        query={{ q }}
        emptyMessage={
          q
            ? `No results for "${q}". Try a different search term.`
            : "Type something above to search."
        }
      />
    </Layout>
  );
}
