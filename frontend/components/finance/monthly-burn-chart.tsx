"use client";

import {
  formatFinanceTooltipLabeledValue,
} from "@/components/finance/chart-tooltip";
import { FinanceChartShell } from "@/components/finance/finance-chart-shell";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { formatMoney } from "@/lib/format-money";
import type { MonthlyBurnOutput } from "@/lib/finance-tool-types";
import { parseToolDecimal } from "@/lib/parse-tool-decimal";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";

const chartConfig = {
  income: {
    label: "Income",
    color: "var(--chart-2)",
  },
  spending: {
    label: "Spending",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig;

interface MonthlyBurnChartProps {
  output: MonthlyBurnOutput;
}

function formatMonth(month: string): string {
  const [year, monthNum] = month.split("-");
  if (!year || !monthNum) {
    return month;
  }

  const parsed = new Date(Number(year), Number(monthNum) - 1, 1);
  if (Number.isNaN(parsed.getTime())) {
    return month;
  }

  return parsed.toLocaleDateString("en-US", { month: "short" });
}

function seriesLabel(name: string): string {
  if (name === "income" || name === chartConfig.income.label) {
    return chartConfig.income.label as string;
  }
  if (name === "spending" || name === chartConfig.spending.label) {
    return chartConfig.spending.label as string;
  }
  return name;
}

/**
 * Grouped bar chart for monthly income vs spending.
 */
export function MonthlyBurnChart({ output }: MonthlyBurnChartProps) {
  const data = output.points.map((point) => ({
    month: point.month,
    income: parseToolDecimal(point.income) ?? 0,
    spending: parseToolDecimal(point.spending) ?? 0,
  }));

  return (
    <FinanceChartShell
      ariaLabel="Monthly income versus spending"
      caption="Monthly income vs spending"
    >
      <ChartContainer
        className="aspect-auto h-full w-full"
        config={chartConfig}
        initialDimension={{ width: 320, height: 128 }}
      >
        <BarChart data={data} margin={{ left: 0, right: 8, top: 4, bottom: 0 }}>
          <CartesianGrid vertical={false} />
          <XAxis
            axisLine={false}
            dataKey="month"
            tickFormatter={formatMonth}
            tickLine={false}
            tickMargin={8}
          />
          <YAxis
            axisLine={false}
            tickFormatter={(value) => formatMoney(Number(value), true)}
            tickLine={false}
            width={48}
          />
          <ChartTooltip
            content={
              <ChartTooltipContent
                formatter={(value, name) =>
                  formatFinanceTooltipLabeledValue(
                    seriesLabel(String(name)),
                    Number(value)
                  )
                }
                labelFormatter={(label) => formatMonth(String(label))}
              />
            }
          />
          <Bar
            dataKey="income"
            fill="var(--color-income)"
            name={chartConfig.income.label as string}
            radius={[2, 2, 0, 0]}
          />
          <Bar
            dataKey="spending"
            fill="var(--color-spending)"
            name={chartConfig.spending.label as string}
            radius={[2, 2, 0, 0]}
          />
        </BarChart>
      </ChartContainer>
    </FinanceChartShell>
  );
}
