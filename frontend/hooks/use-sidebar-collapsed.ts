"use client";

import { SIDEBAR_COLLAPSED_KEY } from "@/lib/constants";
import { useCallback, useSyncExternalStore } from "react";

const listeners = new Set<() => void>();

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSnapshot(): boolean {
  return localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === "true";
}

function getServerSnapshot(): boolean {
  return false;
}

function setStoredCollapsed(collapsed: boolean): void {
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(collapsed));
  for (const listener of listeners) {
    listener();
  }
}

/** Desktop sidebar collapsed state synced with localStorage. */
export function useSidebarCollapsed() {
  const collapsed = useSyncExternalStore(
    subscribe,
    getSnapshot,
    getServerSnapshot
  );

  const setCollapsed = useCallback((value: boolean) => {
    setStoredCollapsed(value);
  }, []);

  return { collapsed, setCollapsed };
}
