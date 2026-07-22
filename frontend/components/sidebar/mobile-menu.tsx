"use client";

import { ConversationList } from "@/components/sidebar/conversation-list";
import { SidebarActions } from "@/components/sidebar/sidebar-actions";
import { SidebarBrandHeader } from "@/components/sidebar/sidebar-brand-header";
import { SidebarFrame } from "@/components/sidebar/sidebar-frame";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { MenuIcon } from "lucide-react";
import { useCallback, useState } from "react";

interface MobileConversationMenuProps {
  activeId: string;
  onSelect: (id: string) => void;
  onNew: () => void;
}

export function MobileConversationMenu({
  activeId,
  onSelect,
  onNew,
}: MobileConversationMenuProps) {
  const [open, setOpen] = useState(false);

  const handleSelect = useCallback(
    (id: string) => {
      onSelect(id);
      setOpen(false);
    },
    [onSelect]
  );

  const handleNew = useCallback(() => {
    onNew();
    setOpen(false);
  }, [onNew]);

  return (
    <Sheet onOpenChange={setOpen} open={open}>
      <SheetTrigger
        aria-label="Open conversations"
        render={
          <Button
            className="relative z-10 size-9"
            size="icon-sm"
            type="button"
            variant="ghost"
          >
            <MenuIcon className="size-4" />
          </Button>
        }
      />
      <SheetContent
        className="flex w-[min(18rem,85vw)] flex-col gap-0 bg-background p-0"
        side="left"
      >
        <SheetTitle className="sr-only">Conversations</SheetTitle>
        <SidebarFrame>
          <SidebarBrandHeader />
          <SidebarActions onNew={handleNew} />
          <ConversationList
            activeId={activeId}
            onNew={handleNew}
            onSelect={handleSelect}
          />
        </SidebarFrame>
      </SheetContent>
    </Sheet>
  );
}
