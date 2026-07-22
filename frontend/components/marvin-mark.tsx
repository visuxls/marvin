import { cn } from "@/lib/utils";
import type { SVGProps } from "react";

type MarvinMarkProps = SVGProps<SVGSVGElement>;

/**
 * Brand mark: an elegant capital M matching the Marvin favicon letterform.
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
      <path
        d="M8.25 8.5v15h2.35v-8.1l5.4 6.35 5.4-6.35v8.1h2.35V8.5h-2.6l-5.15 6.1-5.15-6.1h-2.6z"
        fill="currentColor"
      />
    </svg>
  );
}
