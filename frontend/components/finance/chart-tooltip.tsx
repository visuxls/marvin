import { formatMoney, formatPercent } from "@/lib/format-money";
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

/** Value styling for finance chart tooltips (matches shadcn chart defaults). */
export const financeChartTooltipValueClassName = cn(
  "font-mono font-medium text-foreground tabular-nums"
);

/** Label styling for finance chart tooltip series names. */
export const financeChartTooltipLabelClassName = "text-muted-foreground";

/**
 * Format a dollar amount for chart tooltip values.
 */
export function formatFinanceTooltipValue(value: number): ReactNode {
  return (
    <span className={financeChartTooltipValueClassName}>
      {formatMoney(value)}
    </span>
  );
}

/**
 * Format a labeled tooltip row (e.g. Income: $3,880).
 */
export function formatFinanceTooltipLabeledValue(
  label: string,
  value: number
): ReactNode {
  return (
    <span>
      <span className={financeChartTooltipLabelClassName}>{label}: </span>
      {formatFinanceTooltipValue(value)}
    </span>
  );
}

/**
 * Format a labeled allocation row (e.g. AAPL: $12,500 (28.0%)).
 */
export function formatFinanceTooltipAllocationValue(
  symbol: string,
  value: number,
  weightPct: number
): ReactNode {
  return (
    <span>
      <span className={financeChartTooltipLabelClassName}>{symbol}: </span>
      <span className={financeChartTooltipValueClassName}>
        {formatMoney(value)} ({formatPercent(weightPct)})
      </span>
    </span>
  );
}
