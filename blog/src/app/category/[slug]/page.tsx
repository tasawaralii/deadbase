import type { Metadata } from "next";
import { Layout } from "@/components/Layout";
import { PageBanner } from "@/components/PageBanner";
import { PostList } from "@/components/PostList";
import { getPosts } from "@/lib/posts";
import { slugToLabel } from "@/lib/format";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const label = slugToLabel(decodeURIComponent(slug));
  return {
    title: `${label} Downloads`,
    description: `Browse ${label} anime and cartoons dubbed in Hindi, Tamil, Telugu.`,
  };
}

// "Category" here maps to the Tags taxonomy (Tags.slug) - there is no
// separate category concept in the backend, see app/api/routes/public/post.py.
export default async function CategoryPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { slug } = await params;
  const { page } = await searchParams;
  const currentPage = Number(page) > 0 ? Number(page) : 1;
  const category = decodeURIComponent(slug);
  const { data, limit, count } = await getPosts({ tag: category, page: currentPage });

  return (
    <Layout>
      <PageBanner label={`Category - ${category}`} />
      <PostList
        posts={data}
        page={currentPage}
        limit={limit}
        count={count}
        basePath={`/category/${slug}`}
        emptyMessage="No posts found in this category yet."
      />
    </Layout>
  );
}
