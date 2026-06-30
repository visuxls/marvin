"use client";

import { Button } from "@/components/ui/button";
import { PanelLeftCloseIcon } from "lucide-react";

interface SidebarBrandHeaderProps {
  onCollapse?: () => void;
}

export function SidebarBrandHeader({ onCollapse }: SidebarBrandHeaderProps) {
  return (
    <div className="flex w-full items-center justify-between gap-2 pb-2">
      <h1 className="font-semibold text-base tracking-tight">Marvin</h1>
      {onCollapse && (
        <Button
          aria-label="Collapse sidebar"
          className="text-muted-foreground opacity-60 hover:text-foreground hover:opacity-100"
          onClick={onCollapse}
          size="icon-sm"
          type="button"
          variant="ghost"
        >
          <PanelLeftCloseIcon className="size-4" />
        </Button>
      )}
    </div>
  );
}
