import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface SidebarFrameProps {
  children: ReactNode;
  collapsed?: boolean;
}

export function SidebarFrame({ children, collapsed = false }: SidebarFrameProps) {
  return (
    <div
      className={cn(
        "flex h-full w-full min-w-0 flex-col",
        collapsed ? "items-center p-2" : "p-4"
      )}
    >
      {children}
    </div>
  );
}
