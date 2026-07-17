import type { ReactNode } from "react";
import { Header } from "./Header";
import { Footer } from "./Footer";
import bgHero from "@/assets/bg-hero.jpg";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="relative flex min-h-screen flex-col">
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 -z-10 bg-cover bg-top opacity-40 dark:opacity-20"
        style={{ backgroundImage: `url(${bgHero})` }}
      />
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 -z-10 bg-gradient-to-b from-background/70 via-background/85 to-background"
      />

      <Header />

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6">{children}</main>

      <Footer />
    </div>
  );
}
