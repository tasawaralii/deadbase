import type { Metadata } from "next";
import { Layout } from "@/components/Layout";
import { PageBanner } from "@/components/PageBanner";

export const metadata: Metadata = {
  title: "About Us",
  description: "Learn more about Dead Toons India and what we do.",
};

export default function AboutPage() {
  return (
    <Layout>
      <PageBanner label="About Us" />
      <article className="space-y-6">
        <p className="text-sm leading-relaxed text-foreground/90">
          Dead Toons India is a fan-run destination for anime and cartoons dubbed in Hindi, Tamil, and
          Telugu. We started this site because finding reliable, well-organized dubbed releases used to
          mean digging through a dozen scattered forums and broken links — so we built one place that does
          it properly.
        </p>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">What We Offer</h2>
          <ul className="list-disc pl-5 space-y-2 text-sm leading-relaxed text-foreground/90">
            <li>Hindi, Tamil, and Telugu dubbed anime and cartoons, updated regularly.</li>
            <li>Multiple quality options — 480p, 720p, and 1080p — to fit any connection.</li>
            <li>Dual and multi-audio releases for viewers who like to switch between languages.</li>
            <li>Both completed series and ongoing seasons, tracked episode by episode.</li>
            <li>Movies and OVAs alongside the regular TV catalog.</li>
          </ul>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Our Mission</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            We want dubbed anime to be easy to find and easy to watch, without the clutter and dead links
            that plague most download sites. Every post on Dead Toons India is organized, tagged, and kept
            up to date by our team and community.
          </p>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">A Quick Disclaimer</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            Dead Toons India does not host any files on its own servers. We index and link to content that
            is already available elsewhere on the internet. If you believe something posted here infringes
            your rights, see our{" "}
            <a href="/dmca" className="text-accent hover:underline">
              DMCA page
            </a>{" "}
            for how to request a takedown.
          </p>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Get in Touch</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            Questions, requests, or just want to say hi? Join our Telegram channel from the sidebar or reach
            out through the contact details on our DMCA and Privacy Policy pages.
          </p>
        </div>
      </article>
    </Layout>
  );
}
