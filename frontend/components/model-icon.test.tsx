import { MarvinModelIcon } from "@/components/model-icon";
import { render, screen } from "@testing-library/react";

describe("MarvinModelIcon", () => {
  it("renders a provider initial for known models", () => {
    render(<MarvinModelIcon modelId="openrouter:anthropic/claude-sonnet" />);

    expect(screen.getByText("A")).toBeInTheDocument();
  });

  it("strips the openrouter prefix before resolving the provider", () => {
    render(<MarvinModelIcon modelId="anthropic/claude-sonnet" />);

    expect(screen.getByText("A")).toBeInTheDocument();
  });

  it("falls back to a bot icon for unknown providers", () => {
    const { container } = render(
      <MarvinModelIcon modelId="openrouter:unknown/model" />
    );

    expect(container.querySelector("svg")).toBeInTheDocument();
    expect(screen.queryByText("U")).not.toBeInTheDocument();
  });
});
