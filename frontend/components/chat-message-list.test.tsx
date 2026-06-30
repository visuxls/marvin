import { ChatMessageList } from "@/components/chat-message-list";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UIMessage } from "ai";

vi.mock("@/components/message-part", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/components/message-part")>();
  return {
    ...actual,
    MessagePart: ({ part }: { part: { text?: string } }) => <div>{part.text}</div>,
  };
});

const messages: UIMessage[] = [
  {
    id: "u1",
    role: "user",
    parts: [{ type: "text", text: "Hello Marvin" }],
  },
  {
    id: "a1",
    role: "assistant",
    parts: [{ type: "text", text: "Hello!" }],
  },
];

describe("ChatMessageList", () => {
  it("shows a loading state", () => {
    render(
      <ChatMessageList
        error={undefined}
        isLoadingMessages={true}
        messages={[]}
        onApprovalResponse={vi.fn()}
        onRegenerate={vi.fn()}
        onRetry={vi.fn()}
        status="ready"
      />
    );

    expect(screen.getByText("Loading conversation…")).toBeInTheDocument();
  });

  it("shows the empty state when there are no messages", () => {
    render(
      <ChatMessageList
        error={undefined}
        isLoadingMessages={false}
        messages={[]}
        onApprovalResponse={vi.fn()}
        onRegenerate={vi.fn()}
        onRetry={vi.fn()}
        status="ready"
      />
    );

    expect(
      screen.getByText("How can I help with your finances?")
    ).toBeInTheDocument();
    expect(
      screen.getByText("Pick a starting point below or ask anything.")
    ).toBeInTheDocument();
  });

  it("renders messages", () => {
    render(
      <ChatMessageList
        error={undefined}
        isLoadingMessages={false}
        messages={messages}
        onApprovalResponse={vi.fn()}
        onRegenerate={vi.fn()}
        onRetry={vi.fn()}
        status="ready"
      />
    );

    expect(screen.getByText("Hello Marvin")).toBeInTheDocument();
    expect(screen.getByText("Hello!")).toBeInTheDocument();
  });

  it("hides system messages", () => {
    render(
      <ChatMessageList
        error={undefined}
        isLoadingMessages={false}
        messages={[
          {
            id: "sys",
            role: "system",
            parts: [{ type: "text", text: "Profile: Age 30" }],
          },
          ...messages,
        ]}
        onApprovalResponse={vi.fn()}
        onRegenerate={vi.fn()}
        onRetry={vi.fn()}
        status="ready"
      />
    );

    expect(screen.queryByText("Profile: Age 30")).not.toBeInTheDocument();
    expect(screen.getByText("Hello Marvin")).toBeInTheDocument();
  });

  it("shows thinking indicator while submitted", () => {
    render(
      <ChatMessageList
        error={undefined}
        isLoadingMessages={false}
        messages={messages}
        onApprovalResponse={vi.fn()}
        onRegenerate={vi.fn()}
        onRetry={vi.fn()}
        status="submitted"
      />
    );

    expect(screen.getByText("Thinking…")).toBeInTheDocument();
  });

  it("shows error UI with retry action", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();

    render(
      <ChatMessageList
        error={new Error("Upstream failed")}
        isLoadingMessages={false}
        messages={messages}
        onApprovalResponse={vi.fn()}
        onRegenerate={vi.fn()}
        onRetry={onRetry}
        status="error"
      />
    );

    expect(screen.getByText("Upstream failed")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalled();
  });
});
