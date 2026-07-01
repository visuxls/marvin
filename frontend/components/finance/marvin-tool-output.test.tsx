import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { MarvinToolOutput } from "./marvin-tool-output";

vi.mock("@/components/ai-elements/code-block", () => ({
  CodeBlock: ({ code }: { code: string }) => <pre>{code}</pre>,
}));

describe("MarvinToolOutput", () => {
  it("shows raw JSON in a collapsible section", async () => {
    const user = userEvent.setup();

    render(
      <MarvinToolOutput
        toolPart={{
          type: "tool-get_portfolio_allocation",
          toolCallId: "tool-1",
          state: "output-available",
          input: {},
          output: {
            slices: [
              { symbol: "VOO", market_value: "100", weight_pct: "100" },
            ],
          },
        }}
      />
    );

    expect(screen.queryByText(/"slices"/)).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /raw data/i }));
    expect(screen.getByText(/"slices"/)).toBeInTheDocument();
    expect(screen.queryByTestId("pie-chart")).not.toBeInTheDocument();
  });
});
