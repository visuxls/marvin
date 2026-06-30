import { GET, OPTIONS, PATCH, POST, DELETE } from "@/app/api/[...path]/route";

describe("api proxy route", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ ok: true }), {
          status: 200,
          headers: {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "x-vercel-ai-ui-message-stream": "v1",
          },
        })
      )
    );
  });

  it("proxies GET requests to Marvin", async () => {
    const request = new Request("http://localhost:3000/api/configure?foo=bar");
    const response = await GET(request, {
      params: Promise.resolve({ path: ["configure"] }),
    });

    const fetchMock = vi.mocked(fetch);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const requestUrl = fetchMock.mock.calls[0]?.[0];
    expect(requestUrl).toBeInstanceOf(URL);
    expect((requestUrl as URL).href).toBe(
      "http://127.0.0.1:7932/api/configure?foo=bar"
    );
    expect(fetchMock.mock.calls[0]?.[1]).toMatchObject({ method: "GET" });
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("application/json");
    expect(response.headers.get("cache-control")).toBe("no-cache");
    expect(response.headers.get("x-vercel-ai-ui-message-stream")).toBe("v1");
    await expect(response.json()).resolves.toEqual({ ok: true });
  });

  it("forwards POST bodies with duplex half", async () => {
    const body = JSON.stringify({ prompt: "hello" });
    const request = new Request("http://localhost:3000/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body,
    });

    await POST(request, {
      params: Promise.resolve({ path: ["chat"] }),
    });

    const fetchMock = vi.mocked(fetch);
    const requestUrl = fetchMock.mock.calls[0]?.[0] as URL;
    expect(requestUrl.href).toBe("http://127.0.0.1:7932/api/chat");
    expect(fetchMock.mock.calls[0]?.[1]).toMatchObject({
      method: "POST",
      duplex: "half",
    });
  });

  it("supports PATCH and DELETE", async () => {
    const patchRequest = new Request("http://localhost:3000/api/conversations/1", {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ title: "Updated" }),
    });
    await PATCH(patchRequest, {
      params: Promise.resolve({ path: ["conversations", "1"] }),
    });

    const deleteRequest = new Request("http://localhost:3000/api/conversations/1", {
      method: "DELETE",
    });
    await DELETE(deleteRequest, {
      params: Promise.resolve({ path: ["conversations", "1"] }),
    });

    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("responds to OPTIONS with 200", async () => {
    const response = await OPTIONS();
    expect(response.status).toBe(200);
  });
});
