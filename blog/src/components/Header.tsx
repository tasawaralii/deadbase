"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Search, Menu, X, ChevronDown } from "lucide-react";
import type { GenrePublic, TagPublic } from "@/lib/types";

const NAV_LINKS = [
  { label: "Home", href: "/" },
  { label: "Popular", href: "/?sort=popular" },
  { label: "Movies", href: "/?type=movie" },
  { label: "Series", href: "/?type=tv" },
];

export function Header({ tags, genres }: { tags: TagPublic[]; genres: GenrePublic[] }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [catOpen, setCatOpen] = useState(false);
  const [genreOpen, setGenreOpen] = useState(false);
  const [mobileGenreOpen, setMobileGenreOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (searchOpen) searchInputRef.current?.focus();
  }, [searchOpen]);

  return (
    <>
      <header className="bg-sidebar text-sidebar-foreground sticky top-0 z-40 shadow-md">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-[1fr_auto_1fr] items-center gap-3 h-16">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden justify-self-start p-2 -ml-2 hover:bg-sidebar-accent rounded"
            aria-label="Open menu"
          >
            <Menu className="w-6 h-6" />
          </button>
          <Link href="/" className="flex items-center justify-self-center lg:justify-self-start">
            <Image src="/logo.png" alt="Deadtoons India" width={207} height={63} className="h-11 w-auto" priority />
          </Link>
          <nav className="hidden lg:flex items-center justify-self-center gap-1 font-sans-alt">
            {NAV_LINKS.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="inline-flex items-center gap-1 px-3 py-2 text-sm rounded font-semibold tracking-wide uppercase hover:bg-white hover:text-black transition-colors"
              >
                {item.label}
              </Link>
            ))}

            <div
              className="relative"
              onMouseEnter={() => setCatOpen(true)}
              onMouseLeave={() => setCatOpen(false)}
            >
              <button
                onClick={() => setCatOpen((v) => !v)}
                className="inline-flex items-center gap-1 px-3 py-2 text-sm font-semibold tracking-wide uppercase hover:text-black hover:bg-white transition-color"
              >
                Categories
                <ChevronDown className="w-3 h-3" />
              </button>
              {catOpen && (
                <div className="absolute top-full left-0 min-w-55 max-h-[70vh] overflow-y-auto bg-white text-foreground shadow-xl border-t-2 border-accent z-50">
                  {tags.map((t) => (
                    <Link
                      key={t.slug}
                      href={`/category/${t.slug}`}
                      className="block px-5 py-3 text-sm uppercase tracking-wide border-b border-border hover:text-accent"
                    >
                      {t.name}
                    </Link>
                  ))}
                </div>
              )}
            </div>

            <div
              className="relative"
              onMouseEnter={() => setGenreOpen(true)}
              onMouseLeave={() => setGenreOpen(false)}
            >
              <button
                onClick={() => setGenreOpen((v) => !v)}
                className="inline-flex items-center gap-1 px-3 py-2 text-sm font-semibold tracking-wide uppercase hover:text-black hover:bg-white transition-color"
              >
                Genre
                <ChevronDown className="w-3 h-3" />
              </button>
              {genreOpen && (
                <div className="absolute top-full right-0 min-w-55 max-h-[70vh] overflow-y-auto bg-white text-foreground shadow-xl border-t-2 border-accent z-50">
                  {genres.map((g) => (
                    <Link
                      key={g.slug}
                      href={`/genre/${g.slug}`}
                      className="block px-5 py-3 text-sm uppercase tracking-wide border-b border-border hover:text-accent"
                    >
                      {g.name}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </nav>
          <button
            onClick={() => setSearchOpen((v) => !v)}
            className="justify-self-end p-2 hover:bg-sidebar-accent rounded"
            aria-label="Search"
          >
            {searchOpen ? <X className="w-5 h-5" /> : <Search className="w-5 h-5" />}
          </button>
        </div>
        <form
          action="/search"
          className={`absolute inset-x-0 top-full lg:inset-x-auto lg:right-4 lg:w-96 lg:rounded-b-md bg-white border-t lg:border border-border shadow-lg z-50 transition-all duration-200 ease-out ${
            searchOpen ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2 pointer-events-none"
          }`}
        >
          <div className="max-w-7xl mx-auto px-4 py-3 lg:px-3 flex items-center gap-2">
            <input
              ref={searchInputRef}
              type="search"
              name="q"
              placeholder="Type here to search..."
              className="flex-1 h-12 px-4 border border-border rounded text-foreground bg-white outline-none focus:border-primary"
            />
            <button
              type="submit"
              className="h-12 w-12 grid place-items-center text-foreground hover:text-primary"
              aria-label="Submit search"
            >
              <Search className="w-5 h-5" />
            </button>
          </div>
        </form>
      </header>

      {sidebarOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="fixed top-0 left-0 bottom-0 w-72 bg-sidebar text-sidebar-foreground z-50 overflow-y-auto lg:hidden">
            <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
              <span className="font-display text-lg">MENU</span>
              <button onClick={() => setSidebarOpen(false)} aria-label="Close menu">
                <X className="w-6 h-6" />
              </button>
            </div>
            <nav className="py-2 font-sans-alt">
              {NAV_LINKS.map((item) => (
                <Link
                  key={item.label}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className="block px-5 py-3 text-sm uppercase tracking-wide border-b border-sidebar-border hover:bg-sidebar-accent"
                >
                  {item.label}
                </Link>
              ))}
              {tags.map((t) => (
                <Link
                  key={t.slug}
                  href={`/category/${t.slug}`}
                  onClick={() => setSidebarOpen(false)}
                  className="block px-5 py-3 text-sm uppercase tracking-wide border-b border-sidebar-border hover:bg-sidebar-accent"
                >
                  {t.name}
                </Link>
              ))}
              <button
                onClick={() => setMobileGenreOpen((v) => !v)}
                className="w-full flex items-center justify-between px-5 py-3 text-sm uppercase tracking-wide border-b border-sidebar-border"
              >
                Genre
                <ChevronDown className={`w-4 h-4 transition-transform ${mobileGenreOpen ? "rotate-180" : ""}`} />
              </button>
              {mobileGenreOpen && (
                <div className="bg-black/20">
                  {genres.map((g) => (
                    <Link
                      key={g.slug}
                      href={`/genre/${g.slug}`}
                      onClick={() => setSidebarOpen(false)}
                      className="block pl-8 pr-5 py-2.5 text-sm uppercase tracking-wide border-b border-sidebar-border/50 hover:bg-sidebar-accent"
                    >
                      {g.name}
                    </Link>
                  ))}
                </div>
              )}
            </nav>
          </aside>
        </>
      )}
    </>
  );
}
