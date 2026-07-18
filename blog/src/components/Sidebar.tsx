import Image from "next/image";
import Link from "next/link";
import { getPosts } from "@/lib/posts";

const TELEGRAM_JOIN_URL = process.env.NEXT_PUBLIC_TELEGRAM_JOIN_URL || "#";

export async function Sidebar() {
  const { data: popular } = await getPosts({ sort: "popular", limit: 10 });

  return (
    <aside className="space-y-8">
      <section>
        <div className="border-b-2 border-black">
          <h3 className="bg-black text-primary-foreground inline-block px-3 py-1.5 text-sm font-display font-semibold rounded-sm">
            Follow On Social Media
          </h3>
        </div>
        <div className="mt-3 text-sm text-muted-foreground">
          Follow our <span className="text-accent font-semibold">Fan Channel</span> to get notified about the latest updates.
        </div>
        <a
          href={TELEGRAM_JOIN_URL}
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            src="/join-telegram.png"
            alt="Join us on Telegram"
            width={326}
            height={126}
          />
        </a>
        <p className="mt-3 text-xs font-medium text-muted-foreground">Join our fan channel managed by our fans.</p>
      </section>

      <section>
        <div className="border-b-2 border-black ">
          <h3 className="bg-black text-primary-foreground inline-block px-3 py-1.5 text-sm font-display font-semibold rounded-sm">
            Popular Posts
          </h3>
        </div>
        <ul className="mt-4 space-y-3">
          {popular.map((p) => (
            <li key={p.slug}>
              <Link
                href={`/posts/${p.slug}`}
                className="text-sm font-semibold text-accent hover:underline leading-snug block"
              >
                {p.title}
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </aside>
  );
}
