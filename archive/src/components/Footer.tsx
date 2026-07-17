export function Footer() {
  return (
    <footer className="mt-12 border-t-2 border-border bg-secondary text-secondary-foreground">
      <div className="mx-auto max-w-6xl px-4 py-5 text-center text-xs sm:px-6 sm:text-sm">
        <p className="label-cap text-accent">Disclaimer</p>
        <p className="mt-2">
          <span className="font-display text-base text-primary sm:text-lg">DEADTOONS</span> does not
          host any files. All files are hosted on third-party websites.
        </p>
        <p className="mt-2 font-mono text-[10px] opacity-60 sm:text-xs">
          Team Deadtoons · Demo replica
        </p>
      </div>
    </footer>
  );
}
