import { Send } from "lucide-react";

// Placeholder until wired to the real /public/posts?sort=popular (or similar) endpoint.
const POPULAR = [
  "Alt-Verse Ascendant (Demo) Season 02 Placeholder Multi Audio",
  "Hollow Blade Academy Season 03 Placeholder Audio HQ",
  "Ledger of Shadows (Demo) Season 01 Placeholder Multi Audio",
  "Alt-Verse Ascendant Season 01 (Demo) Placeholder Multi Audio",
  "Ivory Cloverfield (Demo) Season 01 Placeholder Multi Audio",
  "Hollow Blade Academy Season 02 (Demo) Placeholder Multi Audio",
  "Kimeru: Blade of Winter (Demo) Season 01 Placeholder Multi Audio",
  "DAIMA Reborn (Demo) Season 01 Placeholder Multi Audio",
  "Hollow Blade Academy Season 01 Placeholder Two Track Demo",
  "That Life I Woke as Slime (Demo) Season 03 Placeholder Multi Audio",
];

export function Sidebar() {
  return (
    <aside className="space-y-8">
      <section>
        <h3 className="bg-primary text-primary-foreground inline-block px-3 py-1.5 text-sm font-display font-semibold rounded-sm">
          Follow On Social Media
        </h3>
        <div className="mt-3 text-sm text-muted-foreground">
          Follow our <span className="text-accent font-semibold">Fan Channel</span> to get notified about
          latest updates.
        </div>
        <a
          href="#"
          className="mt-4 flex items-center gap-3 border-2 border-primary/20 rounded-md px-4 py-3 hover:border-primary transition-colors"
        >
          <span className="w-10 h-10 rounded-full bg-primary text-primary-foreground grid place-items-center">
            <Send className="w-5 h-5" />
          </span>
          <span className="font-display font-semibold">
            Join us on <span className="text-primary">Telegram</span>
          </span>
        </a>
        <p className="mt-3 text-xs text-muted-foreground">Join our fan channel managed by our fans.</p>
      </section>

      <section>
        <h3 className="bg-primary text-primary-foreground inline-block px-3 py-1.5 text-sm font-display font-semibold rounded-sm">
          Popular Posts
        </h3>
        <ul className="mt-4 space-y-3">
          {POPULAR.map((t) => (
            <li key={t}>
              <a href="#" className="text-sm font-semibold text-accent hover:underline leading-snug block">
                {t}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </aside>
  );
}
