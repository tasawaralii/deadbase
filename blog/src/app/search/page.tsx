import { Search } from "lucide-react";
import { Layout } from "@/components/Layout";
import { PageBanner } from "@/components/PageBanner";
import { PostList } from "@/components/PostList";
import { POSTS } from "@/data/posts";

// Placeholder until wired to GET /api/v1/public/posts/search?q=
export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;

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
      <PostList posts={POSTS} />
    </Layout>
  );
}
