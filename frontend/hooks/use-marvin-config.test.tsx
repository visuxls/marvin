import { useMarvinConfig } from "@/hooks/use-marvin-config";
import { fetchConfigure } from "@/lib/marvin-api";
import { renderHook, waitFor, act } from "@testing-library/react";

vi.mock("@/lib/marvin-api", () => ({
  fetchConfigure: vi.fn(),
}));

describe("useMarvinConfig", () => {
  it("loads config and selects the first model", async () => {
    vi.mocked(fetchConfigure).mockResolvedValue({
      models: [
        { id: "model-a", name: "Model A", builtinTools: [] },
        { id: "model-b", name: "Model B", builtinTools: [] },
      ],
      builtinTools: [],
    });

    const { result } = renderHook(() => useMarvinConfig());

    await waitFor(() => {
      expect(result.current.config?.models).toHaveLength(2);
    });

    expect(result.current.model).toBe("model-a");
  });

  it("leaves state empty when configure fetch fails", async () => {
    vi.mocked(fetchConfigure).mockResolvedValue(null);

    const { result } = renderHook(() => useMarvinConfig());

    await waitFor(() => {
      expect(fetchConfigure).toHaveBeenCalled();
    });

    expect(result.current.config).toBeNull();
    expect(result.current.model).toBe("");
  });

  it("allows changing the selected model", async () => {
    vi.mocked(fetchConfigure).mockResolvedValue({
      models: [
        { id: "model-a", name: "Model A", builtinTools: [] },
        { id: "model-b", name: "Model B", builtinTools: [] },
      ],
      builtinTools: [],
    });

    const { result } = renderHook(() => useMarvinConfig());

    await waitFor(() => {
      expect(result.current.model).toBe("model-a");
    });

    act(() => {
      result.current.setModel("model-b");
    });
    expect(result.current.model).toBe("model-b");
  });
});
