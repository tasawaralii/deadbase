import { Link as RouterLink } from "@tanstack/react-router"
import { ChevronLeft } from "lucide-react"
import type { ReactNode } from "react"

interface PageHeaderProps {
  title: string
  subtitle?: string
  backTo: string
  actions?: ReactNode
}

// A deterministic "back" (always to a named parent route, never
// browser-history) plus title and an optional action slot - used on every
// nested page (anime detail, season detail, ...) so there's always a clear
// way out, especially on mobile where there's no sidebar to fall back on.
export function PageHeader({
  title,
  subtitle,
  backTo,
  actions,
}: PageHeaderProps) {
  return (
    <div className="sticky top-0 z-20 -mx-4 mb-4 flex items-center gap-2 border-b bg-background/95 px-4 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/80 md:static md:mx-0 md:border-none md:bg-transparent md:px-0 md:py-0 md:pb-2 md:backdrop-blur-none">
      <RouterLink
        to={backTo}
        className="-ml-2 flex size-9 shrink-0 items-center justify-center rounded-full text-muted-foreground hover:bg-accent hover:text-foreground"
        aria-label="Back"
      >
        <ChevronLeft className="size-5" />
      </RouterLink>
      <div className="min-w-0 flex-1">
        <h1 className="truncate text-lg font-bold tracking-tight md:text-2xl">
          {title}
        </h1>
        {subtitle && (
          <p className="truncate text-xs text-muted-foreground md:text-sm">
            {subtitle}
          </p>
        )}
      </div>
      {actions && (
        <div className="flex shrink-0 items-center gap-1">{actions}</div>
      )}
    </div>
  )
}
