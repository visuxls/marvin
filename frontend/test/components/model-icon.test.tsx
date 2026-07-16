import { MarvinModelIcon } from "@/components/model-icon";
import { render, screen } from "@testing-library/react";

describe("MarvinModelIcon", () => {
  it("renders the Anthropic brand icon for Claude models", () => {
    const { container } = render(
      <MarvinModelIcon modelId="openrouter:anthropic/claude-sonnet" />
    );

    expect(container.querySelector("svg")).toBeInTheDocument();
    expect(screen.queryByText("A")).not.toBeInTheDocument();
  });

  it("renders the OpenAI brand icon for GPT models", () => {
    const { container } = render(
      <MarvinModelIcon modelId="openrouter:openai/gpt-4.1" />
    );

    expect(container.querySelector("svg")).toBeInTheDocument();
    expect(screen.queryByText("O")).not.toBeInTheDocument();
  });

  it("renders the DeepSeek brand icon for DeepSeek models", () => {
    const { container } = render(
      <MarvinModelIcon modelId="openrouter:deepseek/deepseek-chat" />
    );

    expect(container.querySelector("svg")).toBeInTheDocument();
    expect(screen.queryByText("D")).not.toBeInTheDocument();
  });

  it("renders the Z.AI brand icon for GLM models", () => {
    const { container } = render(
      <MarvinModelIcon modelId="openrouter:z-ai/glm-5.2" />
    );

    expect(container.querySelector("svg")).toBeInTheDocument();
    expect(screen.queryByText("Z")).not.toBeInTheDocument();
  });

  it("renders the xAI brand icon for Grok models", () => {
    const { container } = render(
      <MarvinModelIcon modelId="openrouter:x-ai/grok-4.5" />
    );

    expect(container.querySelector("svg")).toBeInTheDocument();
    expect(screen.queryByText("X")).not.toBeInTheDocument();
  });

  it("strips the openrouter prefix before resolving the provider", () => {
    const { container } = render(
      <MarvinModelIcon modelId="anthropic/claude-sonnet" />
    );

    expect(container.querySelector("svg")).toBeInTheDocument();
  });

  it("falls back to a bot icon for unknown providers", () => {
    const { container } = render(
      <MarvinModelIcon modelId="openrouter:unknown/model" />
    );

    expect(container.querySelector("svg")).toBeInTheDocument();
    expect(screen.queryByText("U")).not.toBeInTheDocument();
  });
});
