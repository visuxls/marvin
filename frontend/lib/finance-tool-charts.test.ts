import { describe, expect, it } from "vitest";

import { extractChartableTools } from "./extract-chartable-tools";
import {
  bucketAllocationSlices,
  getChartableKind,
  normalizeToolName,
} from "./finance-tool-charts";

describe("normalizeToolName", () => {
  it("strips tool- prefix", () => {
    expect(normalizeToolName("tool-get_holdings")).toBe("get_holdings");
  });
});

describe("getChartableKind", () => {
  it("accepts portfolio allocation with two slices", () => {
    const kind = getChartableKind("get_portfolio_allocation", {
      slices: [
        { symbol: "VOO", market_value: "100", weight_pct: "60" },
        { symbol: "BTC", market_value: "50", weight_pct: "40" },
      ],
    });
    expect(kind).toBe("portfolio_allocation");
  });

  it("rejects portfolio allocation with one slice", () => {
    const kind = getChartableKind("get_portfolio_allocation", {
      slices: [{ symbol: "VOO", market_value: "100", weight_pct: "100" }],
    });
    expect(kind).toBeNull();
  });

  it("accepts net worth history with three points", () => {
    const kind = getChartableKind("get_net_worth_over_time", {
      points: [
        { date: "2024-01-01", net_worth_total: "100" },
        { date: "2024-02-01", net_worth_total: "110" },
        { date: "2024-03-01", net_worth_total: "120" },
      ],
    });
    expect(kind).toBe("net_worth_over_time");
  });

  it("rejects monthly burn without data", () => {
    const kind = getChartableKind("get_monthly_burn", {
      has_data: false,
      points: [
        { month: "2024-01", income: "0", spending: "100", net_burn: "100" },
        { month: "2024-02", income: "0", spending: "100", net_burn: "100" },
      ],
    });
    expect(kind).toBeNull();
  });

  it("accepts spending breakdown with four categories", () => {
    const kind = getChartableKind("get_spending_breakdown", {
      has_data: true,
      period_start: "2024-01-01",
      period_end: "2024-03-01",
      categories: [
        { category: "Food", amount: "100", transaction_count: 1, weight_pct: "25" },
        { category: "Rent", amount: "200", transaction_count: 1, weight_pct: "25" },
        { category: "Travel", amount: "50", transaction_count: 1, weight_pct: "25" },
        { category: "Other", amount: "50", transaction_count: 1, weight_pct: "25" },
      ],
    });
    expect(kind).toBe("spending_breakdown");
  });
});

describe("bucketAllocationSlices", () => {
  it("groups tail slices into Other", () => {
    const slices = bucketAllocationSlices(
      [
        { symbol: "A", market_value: "50", weight_pct: "50" },
        { symbol: "B", market_value: "20", weight_pct: "20" },
        { symbol: "C", market_value: "15", weight_pct: "15" },
        { symbol: "D", market_value: "10", weight_pct: "10" },
        { symbol: "E", market_value: "3", weight_pct: "3" },
        { symbol: "F", market_value: "2", weight_pct: "2" },
      ],
      3
    );

    expect(slices).toHaveLength(4);
    expect(slices[3]?.symbol).toBe("Other");
    expect(slices[3]?.marketValue).toBe(15);
    expect(slices[3]?.weightPct).toBe(15);
  });
});

describe("extractChartableTools", () => {
  it("caps charts at two tools in call order", () => {
    const parts = [
      {
        type: "tool-get_portfolio_allocation",
        toolCallId: "1",
        state: "output-available",
        input: {},
        output: {
          slices: [
            { symbol: "VOO", market_value: "100", weight_pct: "60" },
            { symbol: "BTC", market_value: "50", weight_pct: "40" },
          ],
        },
      },
      {
        type: "tool-get_monthly_burn",
        toolCallId: "2",
        state: "output-available",
        input: {},
        output: {
          has_data: true,
          points: [
            { month: "2024-01", income: "1000", spending: "800", net_burn: "-200" },
            { month: "2024-02", income: "1000", spending: "900", net_burn: "-100" },
          ],
        },
      },
      {
        type: "tool-get_spending_breakdown",
        toolCallId: "3",
        state: "output-available",
        input: {},
        output: {
          has_data: true,
          period_start: "2024-01-01",
          period_end: "2024-03-01",
          categories: [
            { category: "Food", amount: "100", transaction_count: 1, weight_pct: "25" },
            { category: "Rent", amount: "200", transaction_count: 1, weight_pct: "25" },
            { category: "Travel", amount: "50", transaction_count: 1, weight_pct: "25" },
            { category: "Other", amount: "50", transaction_count: 1, weight_pct: "25" },
          ],
        },
      },
    ] as const;

    const chartable = extractChartableTools([...parts]);
    expect(chartable).toHaveLength(2);
    expect(chartable[0]?.kind).toBe("portfolio_allocation");
    expect(chartable[1]?.kind).toBe("monthly_burn");
  });

  it("skips tools without chart mappings", () => {
    const parts = [
      {
        type: "tool-get_holdings",
        toolCallId: "1",
        state: "output-available",
        input: {},
        output: { holdings: [] },
      },
    ] as const;

    expect(extractChartableTools([...parts])).toEqual([]);
  });
});
