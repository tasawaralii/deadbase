import type { Metadata } from "next";
import { Layout } from "@/components/Layout";
import { PageBanner } from "@/components/PageBanner";

export const metadata: Metadata = {
  title: "DMCA",
  description: "How to file a DMCA takedown request with Dead Toons India.",
};

export default function DmcaPage() {
  return (
    <Layout>
      <PageBanner label="DMCA" />
      <article className="space-y-6">
        <p className="text-sm leading-relaxed text-foreground/90">
          Dead Toons India does not host any video, audio, or download files on its own servers. We index
          and link to content that is already available on third-party websites. That said, we respect the
          rights of copyright holders and will respond promptly to valid takedown requests under the Digital
          Millennium Copyright Act (DMCA).
        </p>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Filing a Takedown Notice</h2>
          <p className="text-sm leading-relaxed text-foreground/90 mb-3">
            If you believe content linked from this site infringes your copyright, please send a notice that
            includes:
          </p>
          <ol className="list-decimal pl-5 space-y-2 text-sm leading-relaxed text-foreground/90">
            <li>Your name, contact email, and (if applicable) the organization you represent.</li>
            <li>A description of the copyrighted work you believe has been infringed.</li>
            <li>The exact URL(s) on Dead Toons India where the infringing link appears.</li>
            <li>
              A statement that you have a good-faith belief the use is not authorized by the copyright
              owner, its agent, or the law.
            </li>
            <li>
              A statement, made under penalty of perjury, that the information in your notice is accurate
              and that you are the copyright owner or authorized to act on their behalf.
            </li>
            <li>Your physical or electronic signature.</li>
          </ol>
        </div>

        <div className="border border-border rounded p-4 bg-muted">
          <h2 className="font-display font-bold text-lg mb-2">Where to Send Your Notice</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            Email your takedown request to{" "}
            <a href="mailto:dmca@deadtoons.org" className="text-accent font-semibold hover:underline">
              dmca@deadtoons.org
            </a>{" "}
            with the subject line &quot;DMCA Takedown Request&quot;.
          </p>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">What Happens Next</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            We review every valid request and remove or disable links to the reported content, typically
            within a few business days. Incomplete requests may take longer to process while we follow up
            for the missing information.
          </p>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Counter-Notices</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            If you believe content was removed in error, you may submit a counter-notice to the same email
            address, identifying the removed link and explaining why it should be restored.
          </p>
        </div>
      </article>
    </Layout>
  );
}
