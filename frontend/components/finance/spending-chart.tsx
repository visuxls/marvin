"use client";

import { formatFinanceTooltipValue } from "@/components/finance/chart-tooltip";
import { FinanceChartShell } from "@/components/finance/finance-chart-shell";
import { spendingCategoryAxisWidth } from "@/components/finance/spending-chart-axis";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { formatMoney } from "@/lib/format-money";
import type { SpendingBreakdownOutput } from "@/lib/finance-tool-types";
import { parseToolDecimal } from "@/lib/parse-tool-decimal";
import { Bar, BarChart, XAxis, YAxis } from "recharts";

const chartConfig = {
  amount: {
    label: "Spending",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig;

interface SpendingChartProps {
  output: SpendingBreakdownOutput;
}

/**
 * Horizontal bar chart for spending by category.
 */
export function SpendingChart({ output }: SpendingChartProps) {
  const data = [...output.categories]
    .map((category) => ({
      category: category.category,
      amount: parseToolDecimal(category.amount) ?? 0,
    }))
    .sort((a, b) => b.amount - a.amount);
  const yAxisWidth = spendingCategoryAxisWidth(data.map((row) => row.category));

  const caption = `Spending by category (${output.period_start} – ${output.period_end})`;

  return (
    <FinanceChartShell ariaLabel={caption} caption={caption}>
      <ChartContainer
        className="aspect-auto h-full w-full"
        config={chartConfig}
        initialDimension={{ width: 320, height: 128 }}
      >
        <BarChart
          data={data}
          layout="vertical"
          margin={{ left: 0, right: 8, top: 0, bottom: 0 }}
        >
          <XAxis
            axisLine={false}
            tickFormatter={(value) => formatMoney(Number(value), true)}
            tickLine={false}
            type="number"
          />
          <YAxis
            axisLine={false}
            dataKey="category"
            tick={{ fontSize: 11 }}
            tickLine={false}
            type="category"
            width={yAxisWidth}
          />
          <ChartTooltip
            content={
              <ChartTooltipContent
                formatter={(value) => formatFinanceTooltipValue(Number(value))}
              />
            }
          />
          <Bar
            dataKey="amount"
            fill="var(--color-amount)"
            radius={[0, 2, 2, 0]}
          />
        </BarChart>
      </ChartContainer>
    </FinanceChartShell>
  );
}
