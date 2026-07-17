import Image from "next/image";
const TELEGRAM_JOIN_URL = process.env.NEXT_PUBLIC_TELEGRAM_JOIN_URL || "#";

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
