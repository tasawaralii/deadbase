import { Search } from "lucide-react";
import { useState, type FormEvent } from "react";

type Props = {
  className?: string;
  onSubmit?: (query: string) => void;
};

export function SearchBar({ className = "", onSubmit }: Props) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit?.(query.trim());
  };

  return (
    <form
      onSubmit={handleSubmit}
      role="search"
      className={`relative flex items-center ${className}`}
    >
      <Search
        aria-hidden="true"
        className="pointer-events-none absolute left-3 h-4 w-4 text-muted-foreground"
      />
      <input
        type="search"
        name="s"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search anime, episodes…"
        autoComplete="off"
        className="w-full rounded-full border border-border bg-muted/60 py-2 pl-9 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:bg-card focus:outline-none focus:ring-2 focus:ring-ring/40"
      />
    </form>
  );
}
