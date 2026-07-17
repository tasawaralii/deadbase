import Image from "next/image";
import Link from "next/link";
import { Clock, MessageSquare, User, Pin } from "lucide-react";
import { Layout } from "@/components/Layout";

// Placeholder until wired to GET /api/v1/public/posts
type Post = {
  slug: string;
  title: string;
  img: string;
  tags: string[];
  time: string;
  comments: number;
  pinned?: boolean;
};

const POSTS: Post[] = [
  {
    slug: "1",
    img: "/poster-1.jpg",
    pinned: true,
    title:
      "Neon Blossom Nights Season 2 Multi Audio [Placeholder-A/B/C] 480p, 720p & 1080p HD | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Completed"],
    time: "1 day ago",
    comments: 0,
  },
  {
    slug: "2",
    img: "/poster-2.jpg",
    title:
      "Ember Warden Chronicles Season 1 Multi Audio [Placeholder] 480p, 720p & 1080p HD WEB-DL | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Sub Track A", "Regional 1", "Regional 2"],
    time: "1 day ago",
    comments: 3,
  },
  {
    slug: "3",
    img: "/poster-3.jpg",
    title:
      "Frostiron Vanguard Season 1 Dual Audio [Placeholder-A/B] 480p, 720p & 1080p HD WEB-DL | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Ongoing"],
    time: "1 day ago",
    comments: 0,
  },
  {
    slug: "4",
    img: "/poster-4.jpg",
    title: "Sakura Doorstep Diaries (2023) Season 01 Dubbed by Studio Alpha Dual Audio [Placeholder-A/B]",
    tags: ["Dub Pack", "Studio Alpha", "Completed"],
    time: "1 day ago",
    comments: 14,
  },
  {
    slug: "5",
    img: "/poster-1.jpg",
    title:
      "Sakura Doorstep Diaries Season 2 Dual Audio [Placeholder-A/B] 480p, 720p & 1080p HD WEB-DL | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Completed"],
    time: "1 day ago",
    comments: 14,
  },
  {
    slug: "6",
    img: "/poster-2.jpg",
    title: "Ember Warden: Prologue Movie Multi Audio [Placeholder] 1080p HD WEB-DL | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Movie"],
    time: "2 days ago",
    comments: 7,
  },
];

export default function Home() {
  return (
    <Layout>
      <ul className="divide-y divide-border">
        {POSTS.map((p) => (
          <li key={p.slug} className="py-6 flex flex-col sm:flex-row gap-5">
            <Link
              href={`/posts/${p.slug}`}
              className="shrink-0 block sm:w-56 aspect-video overflow-hidden rounded-sm bg-muted"
            >
              <Image
                src={p.img}
                alt=""
                width={1024}
                height={768}
                className="w-full h-full object-cover"
              />
            </Link>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap gap-x-2 gap-y-1 text-sm font-semibold mb-2">
                {p.tags.map((t, i) => (
                  <span key={t} className="text-accent">
                    {t}
                    {i < p.tags.length - 1 && <span className="text-muted-foreground ml-2">·</span>}
                  </span>
                ))}
              </div>
              <h2 className="font-display font-extrabold text-lg sm:text-xl leading-snug text-foreground hover:text-accent transition-colors">
                <Link href={`/posts/${p.slug}`} className="flex gap-2">
                  {p.pinned && <Pin className="w-4 h-4 shrink-0 mt-1.5 text-accent -rotate-45" />}
                  <span>{p.title}</span>
                </Link>
              </h2>
              <div className="flex flex-wrap items-center gap-4 mt-3 text-xs text-muted-foreground">
                <span className="inline-flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {p.time}
                </span>
                <span className="inline-flex items-center gap-1">
                  <MessageSquare className="w-3 h-3" /> {p.comments} Comments
                </span>
                <span className="inline-flex items-center gap-1">
                  <User className="w-3 h-3" /> Admin
                </span>
              </div>
            </div>
          </li>
        ))}
      </ul>

      <div className="flex items-center justify-between mt-8 flex-wrap gap-3">
        <div className="flex items-center gap-1">
          {[1, 2, 3].map((n) => (
            <button
              key={n}
              className={`w-9 h-9 text-sm font-semibold rounded-sm ${
                n === 1 ? "bg-accent text-accent-foreground" : "bg-muted text-foreground hover:bg-border"
              }`}
            >
              {n}
            </button>
          ))}
          <span className="px-2 text-muted-foreground">…</span>
          <button className="w-9 h-9 text-sm font-semibold rounded-sm bg-muted hover:bg-border">42</button>
        </div>
        <button className="bg-accent text-accent-foreground font-semibold text-sm px-6 h-9 rounded-sm hover:opacity-90">
          NEXT ›
        </button>
      </div>
    </Layout>
  );
}
