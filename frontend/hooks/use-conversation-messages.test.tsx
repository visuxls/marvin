import { useConversationMessages } from "@/hooks/use-conversation-messages";
import { fetchConversationMessages } from "@/lib/conversations";
import { renderHook, waitFor } from "@testing-library/react";
import type { UIMessage } from "ai";

vi.mock("@/lib/conversations", () => ({
  fetchConversationMessages: vi.fn(),
}));

describe("useConversationMessages", () => {
  it("loads messages and clears errors when the conversation changes", async () => {
    const messages: UIMessage[] = [
      { id: "m1", role: "user", parts: [{ type: "text", text: "Hi" }] },
    ];
    vi.mocked(fetchConversationMessages).mockResolvedValue(messages);

    const setMessages = vi.fn();
    const clearError = vi.fn();

    const { result } = renderHook(() =>
      useConversationMessages({
        conversationId: "thread-1",
        setMessages,
        clearError,
      })
    );

    expect(result.current.isLoadingMessages).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoadingMessages).toBe(false);
    });

    expect(fetchConversationMessages).toHaveBeenCalledWith("thread-1");
    expect(setMessages).toHaveBeenCalledWith(messages);
    expect(clearError).toHaveBeenCalled();
  });

  it("ignores stale responses after unmount", async () => {
    let resolveFetch: (value: never[]) => void = () => {};
    vi.mocked(fetchConversationMessages).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveFetch = resolve;
        })
    );

    const setMessages = vi.fn();
    const clearError = vi.fn();

    const { unmount } = renderHook(() =>
      useConversationMessages({
        conversationId: "thread-1",
        setMessages,
        clearError,
      })
    );

    unmount();
    resolveFetch([]);

    await Promise.resolve();

    expect(setMessages).not.toHaveBeenCalled();
    expect(clearError).not.toHaveBeenCalled();
  });
});
