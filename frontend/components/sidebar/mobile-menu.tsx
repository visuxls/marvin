"use client";

import { ConversationList } from "@/components/sidebar/conversation-list";
import { SidebarActions } from "@/components/sidebar/sidebar-actions";
import { SidebarBrandHeader } from "@/components/sidebar/sidebar-brand-header";
import { SidebarFrame } from "@/components/sidebar/sidebar-frame";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { MenuIcon } from "lucide-react";

interface MobileConversationMenuProps {
  activeId: string;
  onSelect: (id: string) => void;
  onNew: () => void;
}

export function MobileConversationMenu(props: MobileConversationMenuProps) {
  return (
    <Sheet>
      <SheetTrigger
        aria-label="Open conversations"
        render={
          <Button size="icon-sm" type="button" variant="ghost">
            <MenuIcon className="size-4" />
          </Button>
        }
      />
      <SheetContent className="flex w-72 flex-col gap-0 bg-background p-0" side="left">
        <SidebarFrame>
          <SidebarBrandHeader />
          <SidebarActions onNew={props.onNew} />
          <ConversationList {...props} />
        </SidebarFrame>
      </SheetContent>
    </Sheet>
  );
}
