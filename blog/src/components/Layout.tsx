import type { ReactNode } from "react";
import { Header } from "./Header";
import { Banner } from "./Banner";
import { Sidebar } from "./Sidebar";
import { Footer } from "./Footer";
import { getTags, getGenres } from "@/lib/taxonomy";

export async function Layout({ children }: { children: ReactNode }) {
  const [tags, genres] = await Promise.all([getTags(), getGenres()]);

  return (
    <div className="min-h-screen bg-background text-foreground font-sans flex flex-col">
      <Header tags={tags} genres={genres} />

      <div className="bg-card shadow-[0_0_0_1px_rgba(68,68,68,0.1)] flex flex-col flex-1">
        <Banner />

        <div className="max-w-7xl mx-auto px-4 py-6 grid lg:grid-cols-[1fr_320px] gap-8 flex-1 w-full">
          <main className="min-w-0">{children}</main>
          <Sidebar />
        </div>

        <Footer />
      </div>
    </div>
  );
}
