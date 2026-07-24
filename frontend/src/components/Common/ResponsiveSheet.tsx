import type * as React from "react"

import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer"
import { useIsMobile } from "@/hooks/useMobile"
import { cn } from "@/lib/utils"

// One component, two bodies: a native bottom sheet (drag to dismiss) on
// mobile where every "add X" flow lives, a centered dialog on desktop.
// Same composable shape as Dialog/Drawer so it drops into existing forms.

function ResponsiveSheet({ ...props }: React.ComponentProps<typeof Dialog>) {
  const isMobile = useIsMobile()
  const Root = isMobile ? Drawer : Dialog
  return <Root {...props} />
}

function ResponsiveSheetTrigger({
  ...props
}: React.ComponentProps<typeof DialogTrigger>) {
  const isMobile = useIsMobile()
  const Trigger = isMobile ? DrawerTrigger : DialogTrigger
  return <Trigger {...props} />
}

function ResponsiveSheetContent({
  className,
  children,
  ...props
}: React.ComponentProps<typeof DialogContent>) {
  const isMobile = useIsMobile()
  if (isMobile) {
    return <DrawerContent className={className}>{children}</DrawerContent>
  }
  return (
    <DialogContent className={cn("sm:max-w-lg", className)} {...props}>
      {children}
    </DialogContent>
  )
}

function ResponsiveSheetHeader({
  ...props
}: React.ComponentProps<typeof DialogHeader>) {
  const isMobile = useIsMobile()
  const Header = isMobile ? DrawerHeader : DialogHeader
  return <Header {...props} />
}

function ResponsiveSheetFooter({
  ...props
}: React.ComponentProps<typeof DialogFooter>) {
  const isMobile = useIsMobile()
  const Footer = isMobile ? DrawerFooter : DialogFooter
  return <Footer {...props} />
}

function ResponsiveSheetTitle({
  ...props
}: React.ComponentProps<typeof DialogTitle>) {
  const isMobile = useIsMobile()
  const Title = isMobile ? DrawerTitle : DialogTitle
  return <Title {...props} />
}

function ResponsiveSheetDescription({
  ...props
}: React.ComponentProps<typeof DialogDescription>) {
  const isMobile = useIsMobile()
  const Description = isMobile ? DrawerDescription : DialogDescription
  return <Description {...props} />
}

function ResponsiveSheetClose({
  ...props
}: React.ComponentProps<typeof DialogClose>) {
  const isMobile = useIsMobile()
  const Close = isMobile ? DrawerClose : DialogClose
  return <Close {...props} />
}

export {
  ResponsiveSheet,
  ResponsiveSheetClose,
  ResponsiveSheetContent,
  ResponsiveSheetDescription,
  ResponsiveSheetFooter,
  ResponsiveSheetHeader,
  ResponsiveSheetTitle,
  ResponsiveSheetTrigger,
}
