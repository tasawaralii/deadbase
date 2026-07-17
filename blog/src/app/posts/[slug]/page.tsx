import Image from "next/image";
import Link from "next/link";
import { Layout } from "@/components/Layout";
import { CommentsSection } from "@/components/CommentsSection";

// Placeholder until wired to GET /api/v1/public/posts/{slug}
const POSTERS = ["/poster-1.jpg", "/poster-2.jpg", "/poster-3.jpg", "/poster-4.jpg"];

const RELATED = [
  { slug: "2", title: "Placeholder Movie Alpha (2023) Multi Audio [A-B-C-D]", img: "/poster-2.jpg" },
  {
    slug: "3",
    title: "Placeholder Dark Hero (2017) Official Dubbed Dual Audio [Track A-B] Esubs",
    img: "/poster-3.jpg",
  },
  {
    slug: "4",
    title:
      "The Placeholder Adventures of Demo Rider (2010) Official Dubbed Dual Audio in 480p & 720p & 1080p.",
    img: "/poster-4.jpg",
  },
];

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const idx = (parseInt(slug, 10) - 1) % POSTERS.length;
  const cover = POSTERS[idx >= 0 ? idx : 0];

  return (
    <Layout>
      <article>
        <h1 className="font-display font-semibold text-2xl sm:text-3xl leading-tight mb-4">
          Placeholder Anime Post #{slug} — Multi Audio Demo Release [A-B-C-D] 480p, 720p & 1080p HD WEB-DL |
          10bit HEVC
        </h1>
        <Image
          src={cover}
          alt=""
          width={1280}
          height={720}
          className="w-full aspect-video object-cover rounded-md mb-6"
        />

        <h2 className="font-display font-bold text-xl mb-3">Storyline</h2>
        <p className="text-sm leading-relaxed text-foreground/90 mb-4">
          This is a placeholder storyline standing in until real post content (migrated from the legacy
          blog DB) is wired up.
        </p>

        <section className="mb-10">
          <h2 className="bg-muted inline-block px-3 py-1.5 font-display font-semibold text-sm border-b-2 border-primary">
            You may also like
          </h2>
          <div className="mt-4 space-y-4">
            {RELATED.map((r) => (
              <Link
                key={r.slug}
                href={`/posts/${r.slug}`}
                className="block relative rounded overflow-hidden group"
              >
                <Image src={r.img} alt="" width={1280} height={720} className="w-full aspect-video object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
                <div className="absolute inset-0 grid place-items-center p-6 text-center">
                  <h3 className="text-white font-display font-bold text-lg sm:text-xl leading-tight">
                    {r.title}
                  </h3>
                </div>
              </Link>
            ))}
          </div>
        </section>

        <section className="mb-10 border border-border rounded p-4 flex items-start gap-4">
          <div className="w-16 h-16 rounded-full bg-primary text-primary-foreground grid place-items-center font-display font-bold shrink-0">
            DT
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2 border-b border-border pb-2">
              <h3 className="bg-muted px-3 py-1 text-sm font-display font-semibold">About the author</h3>
              <button className="bg-accent text-accent-foreground text-xs font-bold px-3 py-1.5 uppercase">
                View all posts
              </button>
            </div>
            <div className="font-display font-bold text-lg">Admin</div>
            <p className="text-sm text-muted-foreground">Deadtoons isn&apos;t Dead. So don&apos;t worry.</p>
          </div>
        </section>

        <CommentsSection />
      </article>
    </Layout>
  );
}
