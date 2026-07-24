import { Link as RouterLink, useRouterState } from "@tanstack/react-router"
import type { LucideIcon } from "lucide-react"
import {
  Clapperboard,
  Home,
  MessageSquare,
  Settings,
  Users,
} from "lucide-react"

import { cn } from "@/lib/utils"

type Tab = {
  icon: LucideIcon
  label: string
  path: string
}

const baseTabs: Tab[] = [
  { icon: Home, label: "Home", path: "/" },
  { icon: Clapperboard, label: "Content", path: "/admin/content" },
  { icon: MessageSquare, label: "Comments", path: "/admin/comments" },
  { icon: Settings, label: "Account", path: "/settings" },
]

const superuserTab: Tab = {
  icon: Users,
  label: "People",
  path: "/admin/people",
}

// Primary nav on mobile: a persistent bottom bar, not a hamburger. Every
// top-level destination is one thumb-tap away with zero intermediate state -
// the whole point of moving authors off the laptop.
export function BottomTabBar({ isSuperuser }: { isSuperuser: boolean }) {
  const router = useRouterState()
  const currentPath = router.location.pathname

  const tabs = isSuperuser
    ? [...baseTabs.slice(0, 3), superuserTab, baseTabs[3]]
    : baseTabs

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-30 border-t bg-background pb-[env(safe-area-inset-bottom)] md:hidden"
      aria-label="Primary"
    >
      <div className="flex h-16 items-stretch justify-around">
        {tabs.map((tab) => {
          const isActive =
            tab.path === "/"
              ? currentPath === "/"
              : currentPath.startsWith(tab.path)
          return (
            <RouterLink
              key={tab.path}
              to={tab.path}
              className={cn(
                "flex flex-1 flex-col items-center justify-center gap-1 text-muted-foreground",
                isActive && "text-primary",
              )}
            >
              <tab.icon className="size-5" strokeWidth={isActive ? 2.5 : 2} />
              <span className="text-[11px] font-medium">{tab.label}</span>
            </RouterLink>
          )
        })}
      </div>
    </nav>
  )
}
