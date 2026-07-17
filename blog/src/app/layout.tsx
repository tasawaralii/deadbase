import type { Metadata } from "next";
import { Changa } from "next/font/google";
import "./globals.css";

const changa = Changa({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-changa",
});

export const metadata: Metadata = {
  title: "Deadtoons",
  description: "Deadtoons — anime and cartoons dubbed in Hindi, Tamil, Telugu.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={changa.variable}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
