import { ACTIVE_CONVERSATION_KEY } from "@/lib/constants";
import { useActiveConversation } from "@/hooks/use-active-conversation";
import { act, renderHook } from "@testing-library/react";

vi.mock("nanoid", () => ({
  nanoid: () => "generated-id",
}));

describe("useActiveConversation", () => {
  it("reads the stored conversation id from sessionStorage", () => {
    sessionStorage.setItem(ACTIVE_CONVERSATION_KEY, "stored-id");

    const { result } = renderHook(() => useActiveConversation());

    expect(result.current.conversationId).toBe("stored-id");
  });

  it("generates and stores an id when none exists", () => {
    const { result } = renderHook(() => useActiveConversation());

    expect(result.current.conversationId).toBe("generated-id");
    expect(sessionStorage.getItem(ACTIVE_CONVERSATION_KEY)).toBe("generated-id");
  });

  it("updates subscribers when setConversationId is called", () => {
    const { result } = renderHook(() => useActiveConversation());

    act(() => {
      result.current.setConversationId("new-thread");
    });

    expect(result.current.conversationId).toBe("new-thread");
    expect(sessionStorage.getItem(ACTIVE_CONVERSATION_KEY)).toBe("new-thread");
  });
});
