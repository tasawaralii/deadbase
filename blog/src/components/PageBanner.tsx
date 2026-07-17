export function PageBanner({ label }: { label: string }) {
  return (
    <div className="mb-6">
      <span className="inline-block bg-foreground text-background font-display font-semibold text-sm px-4 py-2">
        {label}
      </span>
      <div className="border-b-2 border-foreground" />
    </div>
  );
}
