export type Post = {
  slug: string;
  title: string;
  img: string;
  tags: string[];
  time: string;
  comments: number;
  pinned?: boolean;
};

// Placeholder until wired to GET /api/v1/public/posts
export const POSTS: Post[] = [
  {
    slug: "1",
    img: "/poster-1.jpg",
    pinned: true,
    title:
      "Neon Blossom Nihts Season 2 Multi Audio [Placeholder-A/B/C] 480p, 720p & 1080p HD | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Completed"],
    time: "1 day ago",
    comments: 0,
  },
  {
    slug: "2",
    img: "/poster-2.jpg",
    title:
      "Ember Warden Chronicles Season 1 Multi Audio [Placeholder] 480p, 720p & 1080p HD WEB-DL | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Sub Track A", "Regional 1", "Regional 2"],
    time: "1 day ago",
    comments: 3,
  },
  {
    slug: "3",
    img: "/poster-3.jpg",
    title:
      "Frostiron Vanguard Season 1 Dual Audio [Placeholder-A/B] 480p, 720p & 1080p HD WEB-DL | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Ongoing"],
    time: "1 day ago",
    comments: 0,
  },
  {
    slug: "4",
    img: "/poster-4.jpg",
    title: "Sakura Doorstep Diaries (2023) Season 01 Dubbed by Studio Alpha Dual Audio [Placeholder-A/B]",
    tags: ["Dub Pack", "Studio Alpha", "Completed"],
    time: "1 day ago",
    comments: 14,
  },
  {
    slug: "5",
    img: "/poster-1.jpg",
    title:
      "Sakura Doorstep Diaries Season 2 Dual Audio [Placeholder-A/B] 480p, 720p & 1080p HD WEB-DL | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Completed"],
    time: "1 day ago",
    comments: 14,
  },
  {
    slug: "6",
    img: "/poster-2.jpg",
    title: "Ember Warden: Prologue Movie Multi Audio [Placeholder] 1080p HD WEB-DL | 10bit HEVC",
    tags: ["Dub Pack", "Studio Alpha", "Movie"],
    time: "2 days ago",
    comments: 7,
  },
];
