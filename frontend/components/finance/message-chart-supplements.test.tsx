import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MessageChartSupplements } from "./message-chart-supplements";

vi.mock("recharts", () => {
  const Mock = ({
    children,
    ...props
  }: {
    children?: React.ReactNode;
  }) => <div {...props}>{children}</div>;

  return {
    ResponsiveContainer: Mock,
    PieChart: Mock,
    Pie: () => <div data-testid="pie" />,
    Cell: () => null,
    LineChart: Mock,
    Line: () => null,
    BarChart: Mock,
    Bar: () => null,
    CartesianGrid: () => null,
    XAxis: () => null,
    YAxis: () => null,
    Tooltip: () => null,
    Legend: () => null,
  };
});

describe("MessageChartSupplements", () => {
  it("renders allocation chart for qualifying tool output", () => {
    render(
      <MessageChartSupplements
        message={{
          id: "a1",
          role: "assistant",
          parts: [
            {
              type: "tool-get_portfolio_allocation",
              toolCallId: "tool-1",
              state: "output-available",
              input: {},
              output: {
                slices: [
                  { symbol: "VOO", market_value: "10000", weight_pct: "60" },
                  { symbol: "BTC", market_value: "5000", weight_pct: "40" },
                ],
              },
            },
          ],
        }}
      />
    );

    expect(screen.getByText("Allocation by market value")).toBeInTheDocument();
    expect(screen.getByTestId("pie")).toBeInTheDocument();
  });

  it("renders nothing when no chartable tools exist", () => {
    const { container } = render(
      <MessageChartSupplements
        message={{
          id: "a1",
          role: "assistant",
          parts: [
            {
              type: "tool-get_holdings",
              toolCallId: "tool-1",
              state: "output-available",
              input: {},
              output: { holdings: [] },
            },
          ],
        }}
      />
    );

    expect(container).toBeEmptyDOMElement();
  });
});
