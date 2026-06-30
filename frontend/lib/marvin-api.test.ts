import { apiUrl, chatApiUrl, fetchConfigure } from "@/lib/marvin-api";

describe("apiUrl", () => {
  it("prefixes paths with the configured API base", () => {
    expect(apiUrl("/api/configure")).toBe("/api/configure");
  });
});

describe("chatApiUrl", () => {
  it("returns the chat endpoint path", () => {
    expect(chatApiUrl()).toBe("/api/chat");
  });
});

describe("fetchConfigure", () => {
  it("returns configure payload on success", async () => {
    const payload = {
      models: [{ id: "m1", name: "Model 1", builtinTools: [] }],
      builtinTools: [],
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => payload,
      })
    );

    await expect(fetchConfigure()).resolves.toEqual(payload);
    expect(fetch).toHaveBeenCalledWith("/api/configure");
  });

  it("returns null on HTTP error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false })
    );

    await expect(fetchConfigure()).resolves.toBeNull();
  });

  it("returns null on network failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    await expect(fetchConfigure()).resolves.toBeNull();
  });
});
