import type { ReactNode } from "react";
import { Header } from "./Header";
import { Banner } from "./Banner";
import { Sidebar } from "./Sidebar";
import { Footer } from "./Footer";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background text-foreground font-sans flex flex-col">
      <Header />
      <Banner />

      <div className="max-w-7xl mx-auto px-4 py-6 grid lg:grid-cols-[1fr_320px] gap-8 flex-1 w-full">
        <main className="min-w-0">{children}</main>
        <Sidebar />
      </div>

      <Footer />
    </div>
  );
}
