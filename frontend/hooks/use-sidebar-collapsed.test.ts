import { SIDEBAR_COLLAPSED_KEY } from "@/lib/constants";
import { act, renderHook } from "@testing-library/react";
import { useSidebarCollapsed } from "@/hooks/use-sidebar-collapsed";

describe("useSidebarCollapsed", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("defaults to expanded", () => {
    const { result } = renderHook(() => useSidebarCollapsed());

    expect(result.current.collapsed).toBe(false);
  });

  it("persists collapsed state in localStorage", () => {
    const { result } = renderHook(() => useSidebarCollapsed());

    act(() => {
      result.current.setCollapsed(true);
    });

    expect(result.current.collapsed).toBe(true);
    expect(localStorage.getItem(SIDEBAR_COLLAPSED_KEY)).toBe("true");

    act(() => {
      result.current.setCollapsed(false);
    });

    expect(result.current.collapsed).toBe(false);
    expect(localStorage.getItem(SIDEBAR_COLLAPSED_KEY)).toBe("false");
  });
});
