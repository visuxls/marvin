import { useMarvinChat } from "@/hooks/use-marvin-chat";
import type { ReasoningEffortId } from "@/lib/marvin-api";
import { renderHook } from "@testing-library/react";

const capturedTransports: Array<{
  body: () => Promise<{ model?: string; reasoningEffort?: string }>;
}> = [];

vi.mock("@ai-sdk/react", () => ({
  useChat: (options: {
    transport: { body: () => Promise<{ model?: string; reasoningEffort?: string }> };
  }) => {
    if (capturedTransports.length === 0) {
      capturedTransports.push(options.transport);
    }
    return {
      status: "ready",
      messages: [],
      sendMessage: vi.fn(),
      stop: vi.fn(),
      setMessages: vi.fn(),
      regenerate: vi.fn(),
      clearError: vi.fn(),
      addToolApprovalResponse: vi.fn(),
      error: undefined,
    };
  },
}));

vi.mock("ai", async (importOriginal) => {
  const actual = await importOriginal<typeof import("ai")>();
  return {
    ...actual,
    DefaultChatTransport: class {
      body: () => Promise<{ model?: string; reasoningEffort?: string }>;

      constructor(options: {
        body: () => { model?: string; reasoningEffort?: string };
      }) {
        this.body = async () => options.body();
      }
    },
    lastAssistantMessageIsCompleteWithApprovalResponses: vi.fn(),
  };
});

describe("useMarvinChat", () => {
  beforeEach(() => {
    capturedTransports.length = 0;
  });

  it("sends the latest selected model even after the picker changes", async () => {
    const { rerender } = renderHook(
      ({ model, reasoningEffort }) =>
        useMarvinChat({
          conversationId: "chat-1",
          model,
          reasoningEffort,
        }),
      {
        initialProps: {
          model: "openrouter:z-ai/glm-5.2",
          reasoningEffort: "off" as ReasoningEffortId,
        },
      }
    );

    expect(capturedTransports).toHaveLength(1);

    rerender({
      model: "openrouter:anthropic/claude-opus-4.8",
      reasoningEffort: "xhigh",
    });

    await expect(capturedTransports[0]!.body()).resolves.toEqual({
      model: "openrouter:anthropic/claude-opus-4.8",
      reasoningEffort: "xhigh",
    });
  });
});
