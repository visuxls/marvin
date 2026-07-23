import { ChatMessageList } from "@/components/chat-message-list";
import { TooltipProvider } from "@/components/ui/tooltip";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";
import type { UIMessage } from "ai";

vi.mock("@/components/message-part", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/components/message-part")>();
  return {
    ...actual,
    MessagePart: ({ part }: { part: { text?: string } }) => <div>{part.text}</div>,
  };
});

function renderList(ui: ReactElement) {
  return render(<TooltipProvider>{ui}</TooltipProvider>);
}

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
    renderList(
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
    renderList(
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
    expect(screen.getByTestId("marvin-mark")).toBeInTheDocument();
  });

  it("renders messages", () => {
    renderList(
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

  it("copies the user prompt to the clipboard", async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", {
      ...navigator,
      clipboard: { writeText },
    });

    renderList(
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

    await user.click(screen.getByRole("button", { name: "Copy prompt" }));
    expect(writeText).toHaveBeenCalledWith("Hello Marvin");
  });

  it("hides system messages", () => {
    renderList(
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
    renderList(
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

    renderList(
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
