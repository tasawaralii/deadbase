"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Search, Menu, X, ChevronDown } from "lucide-react";

const NAV = ["Home", "Latest", "Movies", "Series", "Categories", "Genre"];

const SIDEBAR_LINKS = [
  "Category A",
  "Category B",
  "Dub Studio",
  "Sub Studio",
  "Cartoons",
  "Streaming Alpha",
  "Regional Pack 1",
  "Regional Pack 2",
  "Kids Zone",
  "Live Action",
  "Regional Pack 3",
  "Marvel-ish",
  "Movies",
  "Studio Beta",
  "Streaming Beta",
  "Streaming Gamma",
  "Ongoing",
  "OVA",
  "Kids TV",
  "Legends",
  "Scooby-esque",
  "Sonic-ish",
  "Sony-esque",
  "Specials",
  "Regional Pack 4",
  "Regional Pack 5",
  "Top Picks",
  "Urdu Pack",
  "Voot-ish",
  "Zeecafe-ish",
];

const CATEGORIES = [
  "Alpha",
  "Anime Booth",
  "Apple+",
  "Regional A",
  "Cartoon",
  "Cartoon Network",
  "Kids Cartoon",
  "Completed",
  "Streaming Alpha",
  "Studio Exclusive",
  "Disney",
  "Kids TV",
  "Legends",
  "Sub Track",
  "Movies",
  "Ongoing",
  "OVA",
  "Specials",
];

export function Header() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [catOpen, setCatOpen] = useState(false);
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
            {NAV.map((item) => {
              const isCat = item === "Categories";
              const isGenre = item === "Genre";
              if (isCat) {
                return (
                  <div
                    key={item}
                    className="relative"
                    onMouseEnter={() => setCatOpen(true)}
                    onMouseLeave={() => setCatOpen(false)}
                  >
                    <button
                      onClick={() => setCatOpen((v) => !v)}
                      className="inline-flex items-center gap-1 px-3 py-2 text-sm font-semibold tracking-wide uppercase hover:text-black hover:bg-white transition-color"
                    >
                      {item}
                      <ChevronDown className="w-3 h-3" />
                    </button>
                    {catOpen && (
                      <div className="absolute top-full left-0 min-w-[220px] bg-white text-foreground shadow-xl border-t-2 border-accent z-50">
                        {CATEGORIES.map((c) => (
                          <a
                            key={c}
                            href="#"
                            className="block px-5 py-3 text-sm uppercase tracking-wide border-b border-border hover:text-accent"
                          >
                            {c}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                );
              }
              return (
                <a
                  key={item}
                  href="#"
                  className="inline-flex items-center gap-1 px-3 py-2 text-sm rounded font-semibold tracking-wide uppercase hover:bg-white hover:text-black transition-colors"
                >
                  {item}
                  {isGenre && <ChevronDown className="w-3 h-3" />}
                </a>
              );
            })}
          </nav>
          <button
            onClick={() => setSearchOpen((v) => !v)}
            className="justify-self-end p-2 hover:bg-sidebar-accent rounded"
            aria-label="Search"
          >
            {searchOpen ? <X className="w-5 h-5" /> : <Search className="w-5 h-5" />}
          </button>
        </div>
        <div
          className={`absolute inset-x-0 top-full lg:inset-x-auto lg:right-4 lg:w-96 lg:rounded-b-md bg-white border-t lg:border border-border shadow-lg z-50 transition-all duration-200 ease-out ${
            searchOpen ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2 pointer-events-none"
          }`}
        >
          <div className="max-w-7xl mx-auto px-4 py-3 lg:px-3 flex items-center gap-2">
            <input
              ref={searchInputRef}
              type="search"
              placeholder="Type here to search..."
              className="flex-1 h-12 px-4 border border-border rounded text-foreground bg-white outline-none focus:border-primary"
            />
            <button
              className="h-12 w-12 grid place-items-center text-foreground hover:text-primary"
              aria-label="Submit search"
            >
              <Search className="w-5 h-5" />
            </button>
          </div>
        </div>
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
              {SIDEBAR_LINKS.map((label) => (
                <a
                  key={label}
                  href="#"
                  className="block px-5 py-3 text-sm uppercase tracking-wide border-b border-sidebar-border hover:bg-sidebar-accent"
                >
                  {label}
                </a>
              ))}
              <a
                href="#"
                className="flex items-center justify-between px-5 py-3 text-sm uppercase tracking-wide border-b border-sidebar-border"
              >
                Genre <ChevronDown className="w-4 h-4" />
              </a>
            </nav>
          </aside>
        </>
      )}
    </>
  );
}
