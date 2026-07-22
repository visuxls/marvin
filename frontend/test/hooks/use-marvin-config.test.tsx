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
      reasoningEfforts: [
        { id: "off", label: "Off" },
        { id: "high", label: "High" },
      ],
      defaultReasoningEffort: "off",
    });

    const { result } = renderHook(() => useMarvinConfig());

    await waitFor(() => {
      expect(result.current.config?.models).toHaveLength(2);
    });

    expect(result.current.model).toBe("model-a");
    expect(result.current.reasoningEffort).toBe("off");
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
      reasoningEfforts: [
        { id: "off", label: "Off" },
        { id: "high", label: "High" },
      ],
      defaultReasoningEffort: "off",
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

  it("does not overwrite a model already set before configure resolves", async () => {
    let resolveConfigure: (value: unknown) => void = () => {};
    vi.mocked(fetchConfigure).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveConfigure = resolve;
        })
    );

    const { result } = renderHook(() => useMarvinConfig());

    act(() => {
      result.current.setModel("model-b");
    });

    await act(async () => {
      resolveConfigure({
        models: [
          { id: "model-a", name: "Model A", builtinTools: [] },
          { id: "model-b", name: "Model B", builtinTools: [] },
        ],
        builtinTools: [],
        reasoningEfforts: [{ id: "off", label: "Off" }],
        defaultReasoningEffort: "off",
      });
    });

    await waitFor(() => {
      expect(result.current.config).not.toBeNull();
    });

    expect(result.current.model).toBe("model-b");
  });

  it("allows changing the selected reasoning effort", async () => {
    vi.mocked(fetchConfigure).mockResolvedValue({
      models: [{ id: "model-a", name: "Model A", builtinTools: [] }],
      builtinTools: [],
      reasoningEfforts: [
        { id: "off", label: "Off" },
        { id: "high", label: "High" },
      ],
      defaultReasoningEffort: "off",
    });

    const { result } = renderHook(() => useMarvinConfig());

    await waitFor(() => {
      expect(result.current.reasoningEffort).toBe("off");
    });

    act(() => {
      result.current.setReasoningEffort("high");
    });
    expect(result.current.reasoningEffort).toBe("high");
    expect(localStorage.getItem("marvin:reasoning-effort")).toBe("high");
  });
});
