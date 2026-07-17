import { Layout } from "@/components/Layout";
import { PageBanner } from "@/components/PageBanner";
import { PostList } from "@/components/PostList";
import { POSTS } from "@/data/posts";

// Placeholder until wired to GET /api/v1/public/posts?genre={slug}
export default async function GenrePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;

  return (
    <Layout>
      <PageBanner label={`Genre - ${decodeURIComponent(slug)}`} />
      <PostList posts={POSTS} />
    </Layout>
  );
}
