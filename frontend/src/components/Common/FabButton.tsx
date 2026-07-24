import { Slot } from "@radix-ui/react-slot"
import type { ButtonHTMLAttributes } from "react"

import { cn } from "@/lib/utils"

interface FabButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean
}

// Fixed bottom-right, thumb-reachable on mobile - the single primary action
// for whatever list is on screen (New Anime, Add Episode, Add Links). Sits
// above the bottom tab bar with safe-area padding baked in; on desktop it's
// just a normal floating button since there's no tab bar to clear. Pass
// asChild to make it a RouterLink instead of a click handler - the child
// owns its own icon + label content either way.
export function FabButton({
  asChild = false,
  className,
  children,
  ...props
}: FabButtonProps) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      type={asChild ? undefined : "button"}
      className={cn(
        "fixed right-4 z-40 flex h-14 items-center gap-2 rounded-full bg-primary px-5 text-sm font-semibold text-primary-foreground shadow-lg shadow-black/20 transition-transform active:scale-95 [&_svg]:size-5 [&_svg]:shrink-0",
        "bottom-[calc(4.5rem+env(safe-area-inset-bottom))] md:bottom-6",
        className,
      )}
      {...props}
    >
      {children}
    </Comp>
  )
}
