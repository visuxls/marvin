"use client";

import { formatFinanceTooltipValue } from "@/components/finance/chart-tooltip";
import { FinanceChartShell } from "@/components/finance/finance-chart-shell";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { netWorthYAxisDomain } from "@/lib/chart-axis-domain";
import { formatMoney } from "@/lib/format-money";
import type { NetWorthHistoryOutput } from "@/lib/finance-tool-types";
import { parseToolDecimal } from "@/lib/parse-tool-decimal";
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts";

const chartConfig = {
  netWorth: {
    label: "Net worth",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig;

interface NetWorthChartProps {
  output: NetWorthHistoryOutput;
}

function formatAxisDate(date: string): string {
  const parsed = new Date(`${date}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) {
    return date;
  }

  return parsed.toLocaleDateString("en-US", {
    month: "short",
    year: "2-digit",
  });
}

/**
 * Line chart for net worth over time.
 */
export function NetWorthChart({ output }: NetWorthChartProps) {
  const data = output.points.map((point) => ({
    date: point.date,
    netWorth: parseToolDecimal(point.net_worth_total) ?? 0,
  }));
  const yDomain = netWorthYAxisDomain(data.map((point) => point.netWorth));

  const caption =
    output.investment_values_are_current_snapshot === true
      ? "Net worth over time (investments at current values)"
      : "Net worth over time";

  return (
    <FinanceChartShell ariaLabel={caption} caption={caption}>
      <ChartContainer
        className="aspect-auto h-full w-full"
        config={chartConfig}
        initialDimension={{ width: 320, height: 128 }}
      >
        <LineChart data={data} margin={{ left: 0, right: 8, top: 4, bottom: 0 }}>
          <CartesianGrid vertical={false} />
          <XAxis
            axisLine={false}
            dataKey="date"
            tickFormatter={formatAxisDate}
            tickLine={false}
            tickMargin={8}
          />
          <YAxis
            axisLine={false}
            domain={yDomain}
            tickCount={3}
            tickFormatter={(value) => formatMoney(Number(value), true)}
            tickLine={false}
            width={52}
          />
          <ChartTooltip
            content={
              <ChartTooltipContent
                formatter={(value) => formatFinanceTooltipValue(Number(value))}
                labelFormatter={(label) => formatAxisDate(String(label))}
              />
            }
          />
          <Line
            dataKey="netWorth"
            dot={false}
            stroke="var(--color-netWorth)"
            strokeWidth={2}
            type="monotone"
          />
        </LineChart>
      </ChartContainer>
    </FinanceChartShell>
  );
}
