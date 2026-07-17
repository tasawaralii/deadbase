import { Download } from "lucide-react";
import type { DownloadQuality } from "@/data/episode";
import { Link } from "@tanstack/react-router";

type Props = { item: DownloadQuality };

// Servers carry a semantic color keyword from the admin-configured server_info
// row (danger/warning/etc, Bootstrap-style) - map it to the theme's palette so
// admins control mirror colors without a frontend deploy.
const COLOR_STYLES: Record<string, string> = {
  primary: "bg-primary text-primary-foreground",
  secondary: "bg-secondary text-secondary-foreground",
  danger: "bg-[#dc2626] text-white",
  warning: "bg-[#d97706] text-white",
  success: "bg-[#16a34a] text-white",
  info: "bg-[#0284c7] text-white",
};
const DEFAULT_STYLE = "bg-secondary text-secondary-foreground";

export function DownloadCard({ item }: Props) {
  const [q, ...codec] = item.quality.split(" ");
  return (
    <div className="ticket overflow-hidden">
      <div className="flex items-stretch">
        {/* Left stub — quality badge */}
        <div className="relative flex flex-col items-center justify-center border-r-2 border-dashed border-border bg-accent px-3 py-3 text-accent-foreground sm:px-4">
          <span className="label-cap opacity-70">Quality</span>
          <span className="font-display text-lg leading-none sm:text-2xl">{q}</span>
          <span className="mt-0.5 font-mono text-[10px] font-bold opacity-70">
            {codec.join(" ") || "—"}
          </span>
        </div>

        {/* Body — file meta */}
        <div className="flex min-w-0 flex-1 items-center gap-3 p-3 sm:p-4">
          <div className="min-w-0">
            <p className="label-cap text-muted-foreground">File Size</p>
            <p className="font-mono text-sm font-bold text-foreground sm:text-base">{item.size}</p>
          </div>
          <div className="ml-auto hidden sm:block">
            <span className="label-cap text-muted-foreground">
              {item.links.length} {item.links.length === 1 ? "mirror" : "mirrors"}
            </span>
          </div>
        </div>
      </div>

      {/* Mirrors — capped-width buttons; wrap into rows on all breakpoints */}
      <div className="flex flex-wrap gap-1.5 border-t-2 border-dashed border-border bg-muted/40 p-2 sm:gap-2 sm:p-3">
        {item.links.map((link) => (
          <Link
            key={link.link_server_id}
            to="/unlock"
            search={{ link_server_id: link.link_server_id }}
            className={
              "btn-base w-[calc(50%-0.375rem)] max-w-[11rem] justify-center whitespace-nowrap px-2 py-1.5 text-[11px] sm:w-auto sm:min-w-[9rem] sm:px-3 sm:text-xs " +
              (COLOR_STYLES[link.color] ?? DEFAULT_STYLE)
            }
          >
            <Download className="h-3 w-3 shrink-0 sm:h-3.5 sm:w-3.5" />
            <span>{link.name}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
