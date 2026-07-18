import { Layout } from "@/components/Layout";
import { PageBanner } from "@/components/PageBanner";
import { PostList } from "@/components/PostList";
import { getPosts } from "@/lib/posts";

export default async function AuthorPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { slug } = await params;
  const { page } = await searchParams;
  const currentPage = Number(page) > 0 ? Number(page) : 1;
  const author = decodeURIComponent(slug);
  const { data, limit, count } = await getPosts({ author, page: currentPage });

  return (
    <Layout>
      <PageBanner label={`Author - ${author}`} />
      <PostList
        posts={data}
        page={currentPage}
        limit={limit}
        count={count}
        basePath={`/author/${slug}`}
      />
    </Layout>
  );
}
