"use client";

import { formatFinanceTooltipAllocationValue } from "@/components/finance/chart-tooltip";
import { FinanceChartShell } from "@/components/finance/finance-chart-shell";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import type { AllocationChartSlice } from "@/lib/finance-tool-charts";
import { Cell, Pie, PieChart } from "recharts";

const CHART_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

interface AllocationChartProps {
  slices: AllocationChartSlice[];
}

/**
 * Donut chart for portfolio allocation by symbol.
 */
export function AllocationChart({ slices }: AllocationChartProps) {
  const chartConfig = slices.reduce<ChartConfig>((config, slice, index) => {
    const key = `slice${index}`;
    config[key] = {
      label: slice.symbol,
      color: CHART_COLORS[index % CHART_COLORS.length],
    };
    return config;
  }, {});

  const data = slices.map((slice, index) => ({
    symbol: slice.symbol,
    marketValue: slice.marketValue,
    weightPct: slice.weightPct,
    fill: CHART_COLORS[index % CHART_COLORS.length],
  }));

  return (
    <FinanceChartShell
      ariaLabel="Portfolio allocation by market value"
      caption="Allocation by market value"
    >
      <ChartContainer
        className="aspect-auto h-full w-full"
        config={chartConfig}
        initialDimension={{ width: 320, height: 128 }}
      >
        <PieChart>
          <ChartTooltip
            content={
              <ChartTooltipContent
                formatter={(value, _name, item) => {
                  const payload = item.payload as {
                    symbol: string;
                    weightPct: number;
                  };
                  return formatFinanceTooltipAllocationValue(
                    payload.symbol,
                    Number(value),
                    payload.weightPct
                  );
                }}
                hideLabel
                nameKey="symbol"
              />
            }
          />
          <Pie
            cx="50%"
            cy="50%"
            data={data}
            dataKey="marketValue"
            innerRadius={28}
            nameKey="symbol"
            outerRadius={48}
            strokeWidth={1}
          >
            {data.map((entry) => (
              <Cell fill={entry.fill} key={entry.symbol} />
            ))}
          </Pie>
        </PieChart>
      </ChartContainer>
    </FinanceChartShell>
  );
}
