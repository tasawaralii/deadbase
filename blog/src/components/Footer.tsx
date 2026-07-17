import { Send } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-sidebar text-sidebar-foreground mt-12">
      <div className="max-w-7xl mx-auto px-4 py-10 grid md:grid-cols-2 gap-8">
        <div>
          <h4 className="font-display font-bold text-lg mb-3 border-b border-sidebar-border pb-2">
            About DeadToons
          </h4>
          <p className="text-sm text-white/80 leading-relaxed">
            Dead Toons India avails you all animes, cartoons, in Hindi - Tamil - Telugu dubbed episodes in
            multiple qualities like 1080p, 720p, 480p.
          </p>
          <div className="mt-5 inline-flex items-center gap-3 border-2 border-white/20 rounded-md px-4 py-2">
            <span className="text-sm font-semibold">Join Telegram channel to get the latest news</span>
            <span className="w-8 h-8 rounded-full bg-white text-primary grid place-items-center">
              <Send className="w-4 h-4" />
            </span>
          </div>
        </div>
        <div>
          <h4 className="font-display font-bold text-lg mb-3 border-b border-sidebar-border pb-2">
            Disclaimer
          </h4>
          <p className="text-sm text-white/80 leading-relaxed">
            We do not support piracy. We post the content that is already available on other websites. This
            site does not store any files on its server. All contents are provided by non-affiliated third
            parties. This site does not accept responsibility for contents hosted on third party websites.
            We just index those links which are already available on the internet.
          </p>
          <p className="text-sm text-white/80 leading-relaxed mt-3">
            If you want to remove any post from this website check out our DMCA page
          </p>
        </div>
      </div>
      <div className="border-t border-sidebar-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex flex-wrap items-center justify-between gap-3 text-xs">
          <span className="text-white/60">Copyright DeadToons © 2016 - 2026.</span>
          <div className="flex gap-5 text-white/80 uppercase tracking-wide font-semibold">
            <a href="#" className="hover:text-accent">
              About
            </a>
            <a href="#" className="hover:text-accent">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-accent">
              Request Anime
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
