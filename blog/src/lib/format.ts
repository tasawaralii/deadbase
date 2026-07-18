const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["year", 31536000],
  ["month", 2592000],
  ["week", 604800],
  ["day", 86400],
  ["hour", 3600],
  ["minute", 60],
];

export function timeAgo(iso: string): string {
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return "just now";

  for (const [unit, secondsInUnit] of UNITS) {
    const value = Math.floor(seconds / secondsInUnit);
    if (value >= 1) {
      const rtf = new Intl.RelativeTimeFormat("en", { numeric: "always" });
      return rtf.format(-value, unit);
    }
  }
  return "just now";
}

export function formatCommentDate(iso: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "long",
    timeStyle: "short",
  }).format(new Date(iso));
}

// Standard meta-description length before search engines truncate it anyway.
export function truncate(text: string, maxLength = 160): string {
  const clean = text.trim().replace(/\s+/g, " ");
  if (clean.length <= maxLength) return clean;
  return clean.slice(0, maxLength - 1).trimEnd() + "…";
}

// "eng-subbed" -> "Eng Subbed". Good enough for page titles without an extra
// fetch to look up the tag/genre's real display name.
export function slugToLabel(slug: string): string {
  return slug
    .split("-")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
