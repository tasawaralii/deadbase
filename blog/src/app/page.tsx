import { Layout } from "@/components/Layout";
import { PostList } from "@/components/PostList";
import { getPosts } from "@/lib/posts";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page } = await searchParams;
  const currentPage = Number(page) > 0 ? Number(page) : 1;
  const { data, limit, count } = await getPosts({ page: currentPage });

  return (
    <Layout>
      <PostList posts={data} page={currentPage} limit={limit} count={count} basePath="/" />
    </Layout>
  );
}
