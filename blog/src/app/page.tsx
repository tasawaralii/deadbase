import { Layout } from "@/components/Layout";
import { PostList } from "@/components/PostList";
import { POSTS } from "@/data/posts";

export default function Home() {
  return (
    <Layout>
      <PostList posts={POSTS} />
    </Layout>
  );
}
