import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Search, Send, Home } from "lucide-react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { getTags, getGenres } from "@/lib/taxonomy";

const TELEGRAM_JOIN_URL = process.env.NEXT_PUBLIC_TELEGRAM_JOIN_URL || "#";

export const metadata: Metadata = {
  title: "Page Not Found",
  robots: { index: false, follow: true },
};

export default async function NotFound() {
  const [tags, genres] = await Promise.all([getTags(), getGenres()]);

  return (
    <div className="min-h-screen bg-background text-foreground font-sans flex flex-col">
      <Header tags={tags} genres={genres} />
      <div className="bg-card shadow-[0_0_0_1px_rgba(68,68,68,0.1)] flex flex-col flex-1">
        <main className="flex-1 flex items-center justify-center px-4 py-20">
          <div className="max-w-lg w-full text-center">
            <Image
              src="/logo.png"
              alt="Deadtoons India"
              width={207}
              height={63}
              className="h-12 w-auto mx-auto mb-8"
            />

            <div className="font-display font-extrabold text-8xl sm:text-9xl text-primary leading-none mb-3">
              404
            </div>
            <h1 className="font-display font-semibold text-2xl sm:text-3xl mb-2">
              Looks like you&apos;re lost
            </h1>
            <p className="text-sm text-muted-foreground mb-8">
              The page you were looking for wandered off somewhere. Try searching for what you need
              instead.
            </p>

            <form action="/search" className="flex items-center gap-2 mb-10">
              <input
                type="search"
                name="q"
                placeholder="Search for anime, movies, packs..."
                className="flex-1 h-14 px-5 rounded-md border border-border text-foreground bg-white shadow-sm outline-none focus:border-primary"
              />
              <button
                type="submit"
                className="h-14 w-14 shrink-0 grid place-items-center bg-accent text-accent-foreground rounded-md shadow-sm hover:opacity-90"
                aria-label="Search"
              >
                <Search className="w-5 h-5" />
              </button>
            </form>

            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link
                href="/"
                className="inline-flex items-center gap-2 bg-primary text-primary-foreground font-semibold text-sm px-5 h-11 rounded-sm hover:opacity-90"
              >
                <Home className="w-4 h-4" /> Back To Home
              </Link>
              <a
                href={TELEGRAM_JOIN_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 border-2 border-border font-semibold text-sm px-5 h-11 rounded-sm hover:border-accent hover:text-accent transition-colors"
              >
                <Send className="w-4 h-4" /> Tell Us On Telegram
              </a>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    </div>
  );
}
