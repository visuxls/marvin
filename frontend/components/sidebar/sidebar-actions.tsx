"use client";

import { Button } from "@/components/ui/button";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { useConversations } from "@/contexts/conversations-context";
import { cn } from "@/lib/utils";
import { PlusIcon, SearchIcon } from "lucide-react";
import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";

interface SidebarActionsProps {
  onNew: () => void;
}

export function SidebarActions({ onNew }: SidebarActionsProps) {
  const { searchQuery, setSearchQuery } = useConversations();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const searchContainerRef = useRef<HTMLDivElement>(null);

  const closeSearch = useCallback(() => {
    setIsSearchOpen(false);
    setSearchQuery("");
  }, [setSearchQuery]);

  const toggleSearch = useCallback(() => {
    setIsSearchOpen((open) => {
      if (open) {
        setSearchQuery("");
        return false;
      }
      return true;
    });
  }, [setSearchQuery]);

  const handleNewChat = useCallback(() => {
    closeSearch();
    onNew();
  }, [closeSearch, onNew]);

  useEffect(() => {
    if (isSearchOpen) {
      searchContainerRef.current?.querySelector("input")?.focus();
    }
  }, [isSearchOpen]);

  const handleSearchKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Escape" && !searchQuery.trim()) {
      closeSearch();
    }
  };

  return (
    <div className="w-full shrink-0 pb-3">
      <div className="flex w-full items-center gap-2">
        <Button
          aria-label="New chat"
          className={cn(!isSearchOpen && "flex-1")}
          onClick={handleNewChat}
          size={isSearchOpen ? "icon-sm" : "sm"}
          type="button"
        >
          <PlusIcon className="size-4" />
          {!isSearchOpen && "New Chat"}
        </Button>

        {isSearchOpen && (
          <div className="min-w-0 flex-1" ref={searchContainerRef}>
            <InputGroup className="h-7 w-full rounded-[min(var(--radius-md),12px)]">
              <InputGroupAddon align="inline-start">
                <SearchIcon />
              </InputGroupAddon>
              <InputGroupInput
                className="h-7"
                onChange={(event) => setSearchQuery(event.target.value)}
                onKeyDown={handleSearchKeyDown}
                placeholder="Search chats…"
                type="search"
                value={searchQuery}
              />
            </InputGroup>
          </div>
        )}

        <Button
          aria-label="Search chats"
          aria-pressed={isSearchOpen}
          className={cn(isSearchOpen && "bg-muted")}
          onClick={toggleSearch}
          size="icon-sm"
          type="button"
          variant="outline"
        >
          <SearchIcon className="size-4" />
        </Button>
      </div>
    </div>
  );
}
