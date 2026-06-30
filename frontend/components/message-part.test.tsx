import { ThinkingGroup } from "@/components/message-part";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UIMessage } from "ai";

vi.mock("streamdown", () => ({
  Streamdown: ({ children }: { children: string }) => <div>{children}</div>,
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
        message={message}
      />
    );

    await user.click(screen.getByRole("button", { name: /thought for/i }));

    expect(screen.getByText("Checking holdings.")).toBeInTheDocument();
    expect(screen.getByText("Holdings")).toBeInTheDocument();
    expect(screen.queryByText("You have three positions.")).not.toBeInTheDocument();
  });
});
