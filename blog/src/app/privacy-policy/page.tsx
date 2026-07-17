import { Layout } from "@/components/Layout";
import { PageBanner } from "@/components/PageBanner";

export default function PrivacyPolicyPage() {
  return (
    <Layout>
      <PageBanner label="Privacy Policy" />
      <article className="space-y-6">
        <p className="text-sm leading-relaxed text-foreground/90">
          This Privacy Policy explains what information Dead Toons India collects when you visit the site,
          how we use it, and the choices you have. By using this site, you agree to the practices described
          below.
        </p>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Information We Collect</h2>
          <ul className="list-disc pl-5 space-y-2 text-sm leading-relaxed text-foreground/90">
            <li>
              <span className="font-semibold">Anonymous visitor identifiers.</span> We set a cookie to
              recognize your browser between visits, so features like unlocking downloads and view counts
              work correctly. This cookie is not tied to any account or personal identity.
            </li>
            <li>
              <span className="font-semibold">Comment details.</span> If you leave a comment, we store the
              name, email, and (optional) website you submit along with your comment text.
            </li>
            <li>
              <span className="font-semibold">Basic analytics.</span> We collect aggregate, non-identifying
              data such as page views and referring pages to understand how the site is used.
            </li>
          </ul>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">How We Use This Information</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            We use the information above to operate core site features (like the download unlock system and
            trending lists), moderate comments, and improve the site over time. We do not sell your
            information to third parties.
          </p>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Cookies</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            Dead Toons India uses cookies to remember your visitor identity and unlock progress. You can
            disable cookies in your browser settings, but some features — like unlocking a download without
            repeating a step you already completed — may stop working correctly.
          </p>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Third-Party Links</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            Some links on this site, including download unlock steps, lead to third-party websites (such as
            link shorteners or file hosts) that we do not control. We are not responsible for the privacy
            practices or content of those external sites, and we encourage you to review their own privacy
            policies.
          </p>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Children&apos;s Privacy</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            This site is not directed at children under 13, and we do not knowingly collect personal
            information from children.
          </p>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Changes to This Policy</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            We may update this Privacy Policy from time to time. Any changes will be posted on this page, so
            please check back periodically.
          </p>
        </div>

        <div>
          <h2 className="font-display font-bold text-xl mb-3">Contact Us</h2>
          <p className="text-sm leading-relaxed text-foreground/90">
            If you have questions about this Privacy Policy, you can reach us through our Telegram channel
            linked in the sidebar, or via the contact details on our{" "}
            <a href="/dmca" className="text-accent hover:underline">
              DMCA page
            </a>
            .
          </p>
        </div>
      </article>
    </Layout>
  );
}
