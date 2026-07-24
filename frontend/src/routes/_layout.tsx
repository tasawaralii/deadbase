import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

import { Footer } from "@/components/Common/Footer"
import AppSidebar from "@/components/Sidebar/AppSidebar"
import { BottomTabBar } from "@/components/Sidebar/BottomTabBar"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import { useIsMobile } from "@/hooks/useMobile"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  const isMobile = useIsMobile()
  const { user } = useAuth()

  // Mobile drops the collapsible sidebar entirely in favor of a persistent
  // bottom tab bar - see BottomTabBar for why (zero-tap reachable vs a
  // hamburger's tap-then-wait-then-tap). Desktop keeps the sidebar as-is.
  if (isMobile) {
    return (
      <div className="min-h-dvh bg-background pt-[env(safe-area-inset-top)]">
        <main className="px-4 pb-24 pt-4">
          <Outlet />
        </main>
        <BottomTabBar isSuperuser={!!user?.is_superuser} />
      </div>
    )
  }

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1 text-muted-foreground" />
        </header>
        <main className="flex-1 p-6 md:p-8">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
        <Footer />
      </SidebarInset>
    </SidebarProvider>
  )
}
