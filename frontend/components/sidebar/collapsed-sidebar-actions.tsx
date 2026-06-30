"use client";

import { Button } from "@/components/ui/button";
import { Maximize2Icon, PlusIcon } from "lucide-react";

interface CollapsedSidebarActionsProps {
  onExpand: () => void;
  onNew: () => void;
}

export function CollapsedSidebarActions({
  onExpand,
  onNew,
}: CollapsedSidebarActionsProps) {
  return (
    <div className="flex w-full flex-col items-center gap-2 pt-1">
      <Button
        aria-label="Expand sidebar"
        className="text-muted-foreground opacity-60 hover:text-foreground hover:opacity-100"
        onClick={onExpand}
        size="icon-sm"
        type="button"
        variant="ghost"
      >
        <Maximize2Icon className="size-4" />
      </Button>
      <Button
        aria-label="New chat"
        onClick={onNew}
        size="icon-sm"
        type="button"
      >
        <PlusIcon className="size-4" />
      </Button>
    </div>
  );
}
