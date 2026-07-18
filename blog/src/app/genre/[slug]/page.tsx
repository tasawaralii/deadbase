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
    title: `${label} Anime`,
    description: `Browse ${label} anime and cartoons dubbed in Hindi, Tamil, Telugu.`,
  };
}

export default async function GenrePage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { slug } = await params;
  const { page } = await searchParams;
  const currentPage = Number(page) > 0 ? Number(page) : 1;
  const genre = decodeURIComponent(slug);
  const { data, limit, count } = await getPosts({ genre, page: currentPage });

  return (
    <Layout>
      <PageBanner label={`Genre - ${genre}`} />
      <PostList
        posts={data}
        page={currentPage}
        limit={limit}
        count={count}
        basePath={`/genre/${slug}`}
        emptyMessage="No posts found in this genre yet."
      />
    </Layout>
  );
}
