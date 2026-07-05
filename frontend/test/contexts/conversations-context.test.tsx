import {
  ConversationsProvider,
  useConversations,
} from "@/contexts/conversations-context";
import {
  deleteConversation,
  listConversations,
  togglePinConversation,
  type ConversationEntry,
} from "@/lib/conversations";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";

vi.mock("@/lib/conversations", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/conversations")>();
  return {
    ...actual,
    listConversations: vi.fn(),
    togglePinConversation: vi.fn(),
    deleteConversation: vi.fn(),
  };
});

const sampleEntries: ConversationEntry[] = [
  { id: "1", title: "Net worth", createdAt: 1, pinned: true },
  { id: "2", title: "Holdings", createdAt: 2 },
];

function wrapper({ children }: { children: ReactNode }) {
  return <ConversationsProvider>{children}</ConversationsProvider>;
}

describe("ConversationsProvider", () => {
  beforeEach(() => {
    vi.mocked(listConversations).mockResolvedValue(sampleEntries);
    vi.mocked(togglePinConversation).mockResolvedValue(true);
    vi.mocked(deleteConversation).mockResolvedValue(true);
  });

  it("loads conversations on mount", async () => {
    const { result } = renderHook(() => useConversations(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.entries).toEqual(sampleEntries);
    expect(result.current.pinnedEntries).toHaveLength(1);
    expect(result.current.recentEntries).toHaveLength(1);
  });

  it("filters conversations by search query", async () => {
    const { result } = renderHook(() => useConversations(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.setSearchQuery("hold");
    });

    expect(result.current.filteredEntries).toEqual([sampleEntries[1]]);
    expect(result.current.noMatches).toBe(false);
  });

  it("sets noMatches when search excludes all entries", async () => {
    const { result } = renderHook(() => useConversations(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.setSearchQuery("missing");
    });

    expect(result.current.noMatches).toBe(true);
  });

  it("refreshes after pin and delete actions", async () => {
    const { result } = renderHook(() => useConversations(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.pinConversation("1", true);
    });
    expect(togglePinConversation).toHaveBeenCalledWith("1", true);
    expect(listConversations).toHaveBeenCalled();

    await act(async () => {
      await result.current.deleteConversation("2");
    });
    expect(deleteConversation).toHaveBeenCalledWith("2");
    expect(vi.mocked(listConversations).mock.calls.length).toBeGreaterThanOrEqual(2);
  });

  it("throws when used outside the provider", () => {
    expect(() => renderHook(() => useConversations())).toThrow(
      "useConversations must be used within ConversationsProvider"
    );
  });
});
