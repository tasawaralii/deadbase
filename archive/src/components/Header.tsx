import { Link } from "@tanstack/react-router";
import { Flame, MoonStar, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { SearchBar } from "./SearchBar";
import logo from "@/assets/logo.png";

export function Header() {
  const [dark, setDark] = useState<boolean>(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem("dt-theme");
    const initial = stored
      ? stored === "dark"
      : window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;
    setDark(initial);
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    document.documentElement.classList.toggle("dark", dark);
    try {
      window.localStorage.setItem("dt-theme", dark ? "dark" : "light");
    } catch {}
  }, [dark, mounted]);

  return (
    <header className="sticky top-0 z-40 border-b-2 border-border bg-background/95 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-2 px-3 sm:h-16 sm:gap-3 sm:px-6">
        <Link to="/" className="flex items-center" aria-label="Deadtoons home">
          <img src={logo} alt="Deadtoons" className="h-8 w-auto sm:h-10" />
        </Link>

        <nav className="ml-1 flex items-center sm:ml-3">
          <Link
            to="/trending"
            className="btn-ghost text-foreground"
            activeProps={{ className: "btn-ghost bg-primary text-primary-foreground" }}
          >
            <Flame className="h-4 w-4" />
            <span>Trending</span>
          </Link>
        </nav>

        <div className="ml-auto flex flex-1 items-center justify-end gap-1.5 sm:gap-2">
          <SearchBar className="hidden max-w-sm flex-1 md:flex" />
          <button
            type="button"
            onClick={() => setDark((d) => !d)}
            className="btn-ghost text-foreground"
            aria-label="Toggle theme"
            title="Toggle theme"
          >
            {!mounted ? (
              <span className="block h-4 w-4" aria-hidden />
            ) : dark ? (
              <Sun className="h-4 w-4" />
            ) : (
              <MoonStar className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      <div className="border-t-2 border-border bg-muted/40 px-3 py-2 md:hidden">
        <SearchBar />
      </div>
    </header>
  );
}
