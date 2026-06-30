"use client";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { ConversationEntry } from "@/lib/conversations";
import { formatRelativeTime } from "@/lib/format-relative-time";
import { cn } from "@/lib/utils";
import {
  MoreHorizontalIcon,
  PinIcon,
  PinOffIcon,
  Trash2Icon,
} from "lucide-react";

interface ConversationRowProps {
  entry: ConversationEntry;
  activeId: string;
  onSelect: (id: string) => void;
  onPin: (id: string, currentlyPinned: boolean) => void;
  onDelete: (id: string) => void;
}

export function ConversationRow({
  entry,
  activeId,
  onSelect,
  onPin,
  onDelete,
}: ConversationRowProps) {
  const isActive = entry.id === activeId;
  const isPinned = entry.pinned ?? false;

  return (
    <div className="group relative w-full">
      <button
        className={cn(
          "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors",
          isActive
            ? "bg-sidebar-accent text-sidebar-accent-foreground"
            : "hover:bg-sidebar-accent/50"
        )}
        onClick={() => onSelect(entry.id)}
        type="button"
      >
        <span className="min-w-0 flex-1 truncate font-medium">{entry.title}</span>
        <span
          className={cn(
            "shrink-0 text-muted-foreground text-xs group-hover:invisible",
            isActive && "invisible"
          )}
        >
          {formatRelativeTime(entry.createdAt)}
        </span>
      </button>
      <DropdownMenu>
        <DropdownMenuTrigger
          aria-label="Conversation options"
          className={cn(
            "absolute top-1/2 right-2 -translate-y-1/2 rounded-md p-1 text-muted-foreground opacity-0 transition-opacity hover:bg-background/80 hover:text-foreground group-hover:opacity-100",
            isActive && "opacity-100"
          )}
          onClick={(event) => event.stopPropagation()}
        >
          <MoreHorizontalIcon className="size-4" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-40">
          <DropdownMenuItem
            onClick={() => {
              onPin(entry.id, isPinned);
            }}
          >
            {isPinned ? (
              <>
                <PinOffIcon className="size-4" />
                Unpin
              </>
            ) : (
              <>
                <PinIcon className="size-4" />
                Pin
              </>
            )}
          </DropdownMenuItem>
          <DropdownMenuItem
            className="text-destructive focus:text-destructive"
            onClick={() => {
              onDelete(entry.id);
            }}
          >
            <Trash2Icon className="size-4" />
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
