import type { Metadata } from "next";
import { Layout } from "@/components/Layout";
import { PostList } from "@/components/PostList";
import { getPosts } from "@/lib/posts";

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ type?: string }>;
}): Promise<Metadata> {
  const { type } = await searchParams;
  // The homepage sits at the same segment as the root layout, so its title
  // template doesn't apply here the way it does for nested routes - build
  // the full title explicitly instead of relying on inheritance.
  if (type === "movie") return { title: "Movies | Deadtoons" };
  if (type === "tv") return { title: "Series | Deadtoons" };
  return {};
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; type?: string; sort?: string }>;
}) {
  const { page, type, sort } = await searchParams;
  const currentPage = Number(page) > 0 ? Number(page) : 1;
  const postType = type === "movie" || type === "tv" ? type : undefined;
  const postSort = sort === "popular" ? "popular" : "latest";

  const { data, limit, count } = await getPosts({
    page: currentPage,
    type: postType,
    sort: postSort,
  });

  const query: Record<string, string> = {};
  if (postType) query.type = postType;
  if (sort) query.sort = sort;

  return (
    <Layout>
      <PostList
        posts={data}
        page={currentPage}
        limit={limit}
        count={count}
        basePath="/"
        query={query}
        emptyMessage="No posts available right now. Check back soon for new releases."
      />
    </Layout>
  );
}
