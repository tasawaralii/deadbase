import { Layout } from "@/components/Layout";
import { PageBanner } from "@/components/PageBanner";
import { PostList } from "@/components/PostList";
import { POSTS } from "@/data/posts";

// Placeholder until wired to GET /api/v1/public/posts?category={slug}
export default async function CategoryPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;

  return (
    <Layout>
      <PageBanner label={`Category - ${decodeURIComponent(slug)}`} />
      <PostList posts={POSTS} />
    </Layout>
  );
}
