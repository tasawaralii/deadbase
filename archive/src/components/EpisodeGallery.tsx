import { useEffect, useState } from "react";
import { X } from "lucide-react";

type Props = { images: string[]; title?: string };

export function EpisodeGallery({ images, title = "Stills" }: Props) {
  const [openIdx, setOpenIdx] = useState<number | null>(null);
  const single = images.length === 1;

  useEffect(() => {
    if (openIdx === null) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpenIdx(null);
    };
    window.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [openIdx]);

  if (!images || images.length === 0) return null;

  return (
    <div className="panel overflow-hidden">
      <div className="flex items-center gap-2 border-b-2 border-border bg-muted/50 px-3 py-2 sm:px-4">
        <span className="label-cap text-muted-foreground">{title}</span>
        <span className="ml-auto font-mono text-[10px] font-bold text-muted-foreground">
          {images.length.toString().padStart(2, "0")}
        </span>
      </div>

      {/* mx-auto on a w-max flex row centers when content fits, scrolls when it overflows */}
      <div className="overflow-x-auto">
        <div className="mx-auto flex w-max snap-x snap-mandatory gap-3 p-3 sm:p-4">
          {images.map((src, i) => (
            <button
              key={`${src}-${i}`}
              type="button"
              onClick={() => setOpenIdx(i)}
              className={
                (single ? "w-[16rem] sm:w-[22rem] " : "w-[14rem] sm:w-[18rem] ") +
                "group relative shrink-0 snap-start overflow-hidden border-2 border-border bg-ink"
              }
              aria-label={`Open image ${i + 1}`}
            >
              <img
                src={src}
                alt={`${title} ${i + 1}`}
                loading="lazy"
                className="aspect-video h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
              <span className="absolute left-1.5 top-1.5 border-2 border-border bg-background/90 px-1.5 py-0.5 font-mono text-[9px] font-bold uppercase tracking-widest text-foreground">
                {(i + 1).toString().padStart(2, "0")}
              </span>
            </button>
          ))}
        </div>
      </div>

      {openIdx !== null && (
        <div
          role="dialog"
          aria-modal="true"
          onClick={() => setOpenIdx(null)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
        >
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setOpenIdx(null);
            }}
            aria-label="Close"
            className="absolute right-3 top-3 grid h-10 w-10 place-items-center border-2 border-border bg-background text-foreground hover:bg-primary hover:text-primary-foreground"
          >
            <X className="h-5 w-5" />
          </button>
          <img
            src={images[openIdx]}
            alt={`${title} ${openIdx + 1} full`}
            onClick={(e) => e.stopPropagation()}
            className="max-h-[90vh] max-w-full border-2 border-border object-contain"
          />
        </div>
      )}
    </div>
  );
}
