import Image from "next/image";
import Link from "next/link";
import { Clock, MessageSquare, User } from "lucide-react";
import type { Post } from "@/data/posts";

export function PostList({ posts }: { posts: Post[] }) {
  return (
    <>
      <ul>
        {posts.map((p) => (
          <li key={p.slug} className="py-6 flex flex-col sm:flex-row gap-5">
            <Link
              href={`/posts/${p.slug}`}
              className="shrink-0 block sm:w-64 sm:self-center aspect-video overflow-hidden rounded-sm bg-muted"
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
              <div className="flex flex-wrap gap-x-2 gap-y-1 text-sm font-semibold mb-1.5">
                {p.tags.map((t, i) => (
                  <span key={t} className="text-accent">
                    {t}
                    {i < p.tags.length - 1 && <span className="text-muted-foreground ml-2">·</span>}
                  </span>
                ))}
              </div>
              <h2 className="font-display font-semibold text-2xl sm:text-3xl leading-tight text-foreground hover:text-accent transition-colors">
                <Link href={`/posts/${p.slug}`} className="flex gap-2">
                  <span>{p.title}</span>
                </Link>
              </h2>
              <div className="flex flex-wrap items-center gap-4 mt-4 text-xs font-medium text-muted-foreground">
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
    </>
  );
}
