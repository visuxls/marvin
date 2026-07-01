import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface FinanceChartShellProps {
  caption: string;
  ariaLabel: string;
  children: ReactNode;
  className?: string;
}

/**
 * Subdued wrapper for in-chat finance charts.
 */
export function FinanceChartShell({
  caption,
  ariaLabel,
  children,
  className,
}: FinanceChartShellProps) {
  return (
    <div
      aria-label={ariaLabel}
      className={cn(
        "mt-4 w-full rounded-md border border-border/40 bg-muted/20 px-3 py-2 opacity-90",
        className
      )}
      role="img"
    >
      <p className="mb-2 text-muted-foreground text-xs">{caption}</p>
      <div className="h-32 w-full">{children}</div>
    </div>
  );
}
