import posterImg from "@/assets/episode-poster.jpg";
import backdropImg from "@/assets/episode-backdrop.jpg";
import heroImg from "@/assets/bg-hero.jpg";

export type DownloadLink = {
  label: "HUBCLOUD" | "FILEPRESS" | "CLOUD RESUME" | "GDFLIX" | "PIXELDRAIN";
  href: string;
  variant: "secondary" | "danger" | "warning";
};

export type DownloadQuality = {
  id: string;
  quality: string;
  size: string;
  links: DownloadLink[];
};

export type Episode = {
  animeSlug: string;
  animeTitle: string;
  seasonNumber: number;
  episodeNumber: number;
  title: string;
  description: string;
  poster: string;
  images: string[];
  rating: number;
  releaseDate: string;
  duration: string;
  language: string;
  genres: string[];
  qualities: DownloadQuality[];
};

export const episode: Episode = {
  animeSlug: "tamon-s-b-side",
  animeTitle: "Tamon's B-Side",
  seasonNumber: 1,
  episodeNumber: 1,
  title: "You Need Money to Support Your Oshi",
  description:
    "Utage is a huge fan of Tamon from F/ACE and one day, her work leads her to an unexpected meeting.",
  poster: posterImg,
  images: [backdropImg, backdropImg, backdropImg, backdropImg, backdropImg, backdropImg],
  rating: 8.4,
  releaseDate: "2026-07-02",
  duration: "24 min",
  language: "JP · Subbed",
  genres: ["Romance", "Slice of Life", "Comedy"],
  qualities: [
    {
      id: "480p-x264",
      quality: "480p x264",
      size: "105.4 MB",
      links: [
        { label: "HUBCLOUD", href: "/unlock", variant: "danger" },
      ],
    },
    {
      id: "720p-x265-10bit",
      quality: "720p x265 10bit",
      size: "154.8 MB",
      links: [
        { label: "HUBCLOUD", href: "/unlock", variant: "danger" },
        { label: "FILEPRESS", href: "/unlock", variant: "secondary" },
      ],
    },
    {
      id: "720p-x264",
      quality: "720p x264",
      size: "207.66 MB",
      links: [
        { label: "HUBCLOUD", href: "/unlock", variant: "danger" },
        { label: "FILEPRESS", href: "/unlock", variant: "secondary" },
        { label: "GDFLIX", href: "/unlock", variant: "warning" },
      ],
    },
    {
      id: "1080p-x265-10bit",
      quality: "1080p x265 10bit",
      size: "391.38 MB",
      links: [
        { label: "HUBCLOUD", href: "/unlock", variant: "danger" },
        { label: "FILEPRESS", href: "/unlock", variant: "secondary" },
        { label: "GDFLIX", href: "/unlock", variant: "secondary" },
        { label: "PIXELDRAIN", href: "/unlock", variant: "secondary" },
      ],
    },
    {
      id: "1080p-hq",
      quality: "1080p HQ",
      size: "1.24 GB",
      links: [
        { label: "HUBCLOUD", href: "/unlock", variant: "danger" },
        { label: "FILEPRESS", href: "/unlock", variant: "secondary" },
        { label: "CLOUD RESUME", href: "/unlock-hq", variant: "secondary" },
        { label: "GDFLIX", href: "/unlock", variant: "secondary" },
        { label: "PIXELDRAIN", href: "/unlock", variant: "secondary" },
      ],
    },
  ],
};

export type TrendingEpisode = {
  animeSlug: string;
  animeTitle: string;
  seasonNumber: number;
  episodeNumber: number;
  title: string;
  rating: number;
  releaseDate: string;
  poster: string;
};

export const trendingEpisodes: TrendingEpisode[] = [
  {
    animeSlug: "tamon-s-b-side",
    animeTitle: "Tamon's B-Side",
    seasonNumber: 1,
    episodeNumber: 1,
    title: "You Need Money to Support Your Oshi",
    rating: 8.4,
    releaseDate: "2026-07-02",
    poster: backdropImg,
  },
  {
    animeSlug: "tamon-s-b-side",
    animeTitle: "Tamon's B-Side",
    seasonNumber: 1,
    episodeNumber: 2,
    title: "The First Meeting",
    rating: 8.2,
    releaseDate: "2026-07-03",
    poster: backdropImg,
  },
  {
    animeSlug: "tamon-s-b-side",
    animeTitle: "Tamon's B-Side",
    seasonNumber: 1,
    episodeNumber: 3,
    title: "Backstage Pass",
    rating: 8.6,
    releaseDate: "2026-07-04",
    poster: backdropImg,
  },
  {
    animeSlug: "tamon-s-b-side",
    animeTitle: "Tamon's B-Side",
    seasonNumber: 1,
    episodeNumber: 4,
    title: "A Fan's Dilemma",
    rating: 8.1,
    releaseDate: "2026-07-05",
    poster: backdropImg,
  },
  {
    animeSlug: "tamon-s-b-side",
    animeTitle: "Tamon's B-Side",
    seasonNumber: 1,
    episodeNumber: 5,
    title: "Under the Stage Lights",
    rating: 8.7,
    releaseDate: "2026-07-06",
    poster: backdropImg,
  },
  {
    animeSlug: "tamon-s-b-side",
    animeTitle: "Tamon's B-Side",
    seasonNumber: 1,
    episodeNumber: 6,
    title: "Between the Notes",
    rating: 8.5,
    releaseDate: "2026-07-07",
    poster: backdropImg,
  },
  {
    animeSlug: "tamon-s-b-side",
    animeTitle: "Tamon's B-Side",
    seasonNumber: 1,
    episodeNumber: 7,
    title: "Encore",
    rating: 8.9,
    releaseDate: "2026-07-08",
    poster: backdropImg,
  },
];
