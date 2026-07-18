"use client";

import { useState } from "react";
import { X } from "lucide-react";

export function Banner() {
  const [open, setOpen] = useState(true);
  if (!open) return null;

  return (
    <div className="max-w-7xl mx-auto px-4 pt-4">
      <div className="bg-success text-success-foreground rounded-md px-4 py-3 flex items-center justify-between text-sm font-semibold">
        <span className="mx-auto text-center">
          Always use{" "}
          <a href="https://deadtoons.org" className="text-primary underline">
            Deadtoons.org
          </a>{" "}
          with VPN to get the official domain.
        </span>
        <button
          onClick={() => setOpen(false)}
          className="ml-3 shrink-0 opacity-70 hover:opacity-100"
          aria-label="Dismiss banner"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
