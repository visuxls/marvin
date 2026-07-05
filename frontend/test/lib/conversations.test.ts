import {
  deleteConversation,
  fetchConversationMessages,
  filterConversations,
  listConversations,
  togglePinConversation,
  updateConversation,
  type ConversationEntry,
} from "@/lib/conversations";

const entries: ConversationEntry[] = [
  { id: "1", title: "Net worth check", createdAt: 1_700_000_000_000 },
  { id: "2", title: "Holdings review", createdAt: 1_700_000_100_000, pinned: true },
  { id: "3", title: "Tax planning", createdAt: 1_700_000_200_000 },
];

describe("filterConversations", () => {
  it("returns all entries when query is empty", () => {
    expect(filterConversations(entries, "")).toEqual(entries);
    expect(filterConversations(entries, "   ")).toEqual(entries);
  });

  it("filters by title case-insensitively", () => {
    expect(filterConversations(entries, "holdings")).toEqual([entries[1]]);
    expect(filterConversations(entries, "NET")).toEqual([entries[0]]);
  });

  it("returns empty array when nothing matches", () => {
    expect(filterConversations(entries, "crypto")).toEqual([]);
  });
});

describe("listConversations", () => {
  it("returns parsed conversations on success", async () => {
    const payload = [{ id: "a", title: "Chat", createdAt: 1 }];
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => payload,
      })
    );

    await expect(listConversations()).resolves.toEqual(payload);
    expect(fetch).toHaveBeenCalledWith("/api/conversations");
  });

  it("returns empty array on HTTP error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false })
    );

    await expect(listConversations()).resolves.toEqual([]);
  });

  it("returns empty array on network failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    await expect(listConversations()).resolves.toEqual([]);
  });
});

describe("fetchConversationMessages", () => {
  it("returns messages from the API payload", async () => {
    const messages = [{ id: "m1", role: "user", parts: [{ type: "text", text: "Hi" }] }];
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ messages }),
      })
    );

    await expect(fetchConversationMessages("thread-1")).resolves.toEqual(messages);
    expect(fetch).toHaveBeenCalledWith("/api/conversations/thread-1/messages");
  });

  it("drops system messages from the API payload", async () => {
    const messages = [
      {
        id: "sys",
        role: "system",
        parts: [{ type: "text", text: "Profile: Age 30" }],
      },
      { id: "m1", role: "user", parts: [{ type: "text", text: "Hi" }] },
    ];
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ messages }),
      })
    );

    await expect(fetchConversationMessages("thread-1")).resolves.toEqual([messages[1]]);
  });

  it("encodes conversation ids in the URL", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ messages: [] }),
      })
    );

    await fetchConversationMessages("a/b c");
    expect(fetch).toHaveBeenCalledWith("/api/conversations/a%2Fb%20c/messages");
  });

  it("returns empty array on failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false })
    );

    await expect(fetchConversationMessages("x")).resolves.toEqual([]);
  });
});

describe("updateConversation", () => {
  it("PATCHes partial fields and returns success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true })
    );

    await expect(updateConversation("id-1", { title: "Renamed" })).resolves.toBe(true);
    expect(fetch).toHaveBeenCalledWith("/api/conversations/id-1", {
      body: JSON.stringify({ title: "Renamed" }),
      headers: { "Content-Type": "application/json" },
      method: "PATCH",
    });
  });

  it("returns false on failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    await expect(updateConversation("id-1", { pinned: true })).resolves.toBe(false);
  });
});

describe("togglePinConversation", () => {
  it("flips the pinned flag", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true })
    );

    await togglePinConversation("id-1", false);
    expect(fetch).toHaveBeenCalledWith("/api/conversations/id-1", {
      body: JSON.stringify({ pinned: true }),
      headers: { "Content-Type": "application/json" },
      method: "PATCH",
    });
  });
});

describe("deleteConversation", () => {
  it("DELETEs the conversation", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true })
    );

    await expect(deleteConversation("id-1")).resolves.toBe(true);
    expect(fetch).toHaveBeenCalledWith("/api/conversations/id-1", {
      method: "DELETE",
    });
  });

  it("returns false on failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false })
    );

    await expect(deleteConversation("id-1")).resolves.toBe(false);
  });
});
