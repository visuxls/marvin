import { cn } from "@/lib/utils";
import type { SVGProps } from "react";

type MarvinMarkProps = SVGProps<SVGSVGElement>;

/**
 * Brand mark: M fused with three ascending chart bars (C1).
 *
 * Three columns share a baseline; slanted tops form an M silhouette
 * while the overall rise reads as portfolio growth.
 */
export function MarvinMark({ className, ...props }: MarvinMarkProps) {
  return (
    <svg
      aria-hidden
      className={cn("shrink-0", className)}
      data-testid="marvin-mark"
      fill="none"
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path d="M6.25 24.5V8.25L12 15.75V24.5H6.25Z" fill="currentColor" />
      <path d="M13.25 24.5V16.5L19 12.78V24.5H13.25Z" fill="currentColor" />
      <path d="M20.25 24.5V11.97L26 8.25V24.5H20.25Z" fill="currentColor" />
    </svg>
  );
}
