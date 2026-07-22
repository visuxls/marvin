import { MessagePart, ThinkingGroup } from "@/components/message-part";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UIMessage } from "ai";

vi.mock("streamdown", () => ({
  Streamdown: ({
    children,
    mode,
  }: {
    children: string;
    mode?: string;
  }) => <div data-mode={mode ?? "static"}>{children}</div>,
}));

describe("ThinkingGroup", () => {
  it("nests tool calls inside the thinking section", async () => {
    const user = userEvent.setup();
    const message: UIMessage = {
      id: "a1",
      role: "assistant",
      parts: [
        { type: "reasoning", text: "Checking holdings." },
        {
          type: "tool-get_holdings",
          toolCallId: "tool-1",
          state: "output-available",
          input: {},
          output: { holdings: [] },
        },
        { type: "text", text: "You have three positions." },
      ],
    };

    render(
      <ThinkingGroup
        chatStatus="ready"
        group={{
          type: "thinking",
          startIndex: 0,
          parts: message.parts.slice(0, 2),
        }}
        isLastMessage={false}
        message={message}
      />
    );

    await user.click(screen.getByRole("button", { name: /thought for/i }));

    expect(screen.getByText("Checking holdings.")).toBeInTheDocument();
    expect(screen.getByText("Checking holdings.")).toHaveAttribute(
      "data-mode",
      "static"
    );
    expect(screen.getByText("Holdings")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /holdings/i }));
    expect(screen.getByRole("button", { name: /raw data/i })).toBeInTheDocument();
    expect(screen.queryByText("You have three positions.")).not.toBeInTheDocument();
  });

  it("renders plain text while reasoning is streaming", () => {
    const message: UIMessage = {
      id: "a2",
      role: "assistant",
      parts: [{ type: "reasoning", text: "Still thinking about Austin…" }],
    };

    render(
      <ThinkingGroup
        chatStatus="streaming"
        group={{
          type: "thinking",
          startIndex: 0,
          parts: message.parts,
        }}
        isLastMessage={true}
        message={message}
      />
    );

    const text = screen.getByText("Still thinking about Austin…");
    expect(text.tagName).toBe("P");
    expect(text).not.toHaveAttribute("data-mode");
  });
});

describe("MessagePart", () => {
  it("uses static mode for older assistant messages while streaming", () => {
    const priorAssistant: UIMessage = {
      id: "a1",
      role: "assistant",
      parts: [{ type: "text", text: "Earlier reply" }],
    };

    render(
      <MessagePart
        chatStatus="streaming"
        isLastAssistantPart={true}
        isLastMessage={false}
        message={priorAssistant}
        onRegenerate={vi.fn()}
        part={priorAssistant.parts[0]}
      />
    );

    expect(screen.getByText("Earlier reply")).toHaveAttribute(
      "data-mode",
      "static"
    );
  });

  it("uses streaming mode only for the active assistant message", () => {
    const activeAssistant: UIMessage = {
      id: "a2",
      role: "assistant",
      parts: [{ type: "text", text: "New reply" }],
    };

    render(
      <MessagePart
        chatStatus="streaming"
        isLastAssistantPart={true}
        isLastMessage={true}
        message={activeAssistant}
        onRegenerate={vi.fn()}
        part={activeAssistant.parts[0]}
      />
    );

    expect(screen.getByText("New reply")).toHaveAttribute(
      "data-mode",
      "streaming"
    );
  });
});
