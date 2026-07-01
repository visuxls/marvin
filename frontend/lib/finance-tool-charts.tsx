import { AllocationChart } from "@/components/finance/allocation-chart";
import { MonthlyBurnChart } from "@/components/finance/monthly-burn-chart";
import { NetWorthChart } from "@/components/finance/net-worth-chart";
import { SpendingChart } from "@/components/finance/spending-chart";
import { parseToolDecimal } from "@/lib/parse-tool-decimal";
import type {
  ChartableToolKind,
  MonthlyBurnOutput,
  NetWorthHistoryOutput,
  PortfolioAllocationOutput,
  SpendingBreakdownOutput,
} from "@/lib/finance-tool-types";
import type { ReactNode } from "react";

const MAX_ALLOCATION_SLICES = 5;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isPortfolioAllocationOutput(
  output: unknown
): output is PortfolioAllocationOutput {
  if (!isRecord(output) || !Array.isArray(output.slices)) {
    return false;
  }

  return output.slices.length >= 2;
}

function isNetWorthHistoryOutput(
  output: unknown
): output is NetWorthHistoryOutput {
  if (!isRecord(output) || !Array.isArray(output.points)) {
    return false;
  }

  return output.points.length >= 3;
}

function isMonthlyBurnOutput(output: unknown): output is MonthlyBurnOutput {
  if (!isRecord(output) || !Array.isArray(output.points)) {
    return false;
  }

  return output.has_data === true && output.points.length >= 2;
}

function isSpendingBreakdownOutput(
  output: unknown
): output is SpendingBreakdownOutput {
  if (!isRecord(output) || !Array.isArray(output.categories)) {
    return false;
  }

  return output.has_data === true && output.categories.length >= 4;
}

/**
 * Normalize backend tool name from UI part type or dynamic tool name.
 */
export function normalizeToolName(toolNameOrType: string): string {
  if (toolNameOrType.startsWith("tool-")) {
    return toolNameOrType.slice("tool-".length);
  }

  return toolNameOrType;
}

/**
 * Return chart kind when output qualifies for visualization.
 */
export function getChartableKind(
  toolName: string,
  output: unknown
): ChartableToolKind | null {
  const normalized = normalizeToolName(toolName);

  switch (normalized) {
    case "get_portfolio_allocation":
      return isPortfolioAllocationOutput(output) ? "portfolio_allocation" : null;
    case "get_net_worth_over_time":
      return isNetWorthHistoryOutput(output) ? "net_worth_over_time" : null;
    case "get_monthly_burn":
      return isMonthlyBurnOutput(output) ? "monthly_burn" : null;
    case "get_spending_breakdown":
      return isSpendingBreakdownOutput(output) ? "spending_breakdown" : null;
    default:
      return null;
  }
}

export type AllocationChartSlice = {
  symbol: string;
  marketValue: number;
  weightPct: number;
};

/**
 * Bucket allocation slices to top N plus Other.
 */
export function bucketAllocationSlices(
  slices: PortfolioAllocationOutput["slices"],
  maxSlices = MAX_ALLOCATION_SLICES
): AllocationChartSlice[] {
  const parsed = slices
    .map((slice) => ({
      symbol: slice.symbol,
      marketValue: parseToolDecimal(slice.market_value) ?? 0,
      weightPct: parseToolDecimal(slice.weight_pct) ?? 0,
    }))
    .sort((a, b) => b.marketValue - a.marketValue);

  if (parsed.length <= maxSlices) {
    return parsed;
  }

  const top = parsed.slice(0, maxSlices);
  const rest = parsed.slice(maxSlices);
  const otherMarketValue = rest.reduce((sum, slice) => sum + slice.marketValue, 0);
  const otherWeightPct = rest.reduce((sum, slice) => sum + slice.weightPct, 0);

  return [
    ...top,
    {
      symbol: "Other",
      marketValue: otherMarketValue,
      weightPct: otherWeightPct,
    },
  ];
}

/**
 * Resolve a chart React node for a qualifying tool output.
 */
export function resolveToolChart(
  toolName: string,
  output: unknown
): ReactNode | null {
  const kind = getChartableKind(toolName, output);
  if (!kind) {
    return null;
  }

  switch (kind) {
    case "portfolio_allocation":
      return (
        <AllocationChart
          slices={bucketAllocationSlices(
            (output as PortfolioAllocationOutput).slices
          )}
        />
      );
    case "net_worth_over_time":
      return (
        <NetWorthChart output={output as NetWorthHistoryOutput} />
      );
    case "monthly_burn":
      return <MonthlyBurnChart output={output as MonthlyBurnOutput} />;
    case "spending_breakdown":
      return (
        <SpendingChart output={output as SpendingBreakdownOutput} />
      );
    default:
      return null;
  }
}
