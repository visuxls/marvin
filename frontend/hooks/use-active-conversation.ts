"use client";

import {
  ACTIVE_CONVERSATION_KEY,
  SERVER_CONVERSATION_PLACEHOLDER,
} from "@/lib/constants";
import { nanoid } from "nanoid";
import { useCallback, useSyncExternalStore } from "react";

const listeners = new Set<() => void>();

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSnapshot(): string {
  let id = sessionStorage.getItem(ACTIVE_CONVERSATION_KEY);
  if (!id) {
    id = nanoid();
    sessionStorage.setItem(ACTIVE_CONVERSATION_KEY, id);
  }
  return id;
}

function getServerSnapshot(): string {
  return SERVER_CONVERSATION_PLACEHOLDER;
}

function setStoredConversationId(id: string): void {
  sessionStorage.setItem(ACTIVE_CONVERSATION_KEY, id);
  for (const listener of listeners) {
    listener();
  }
}

/** Active conversation id synced with sessionStorage. */
export function useActiveConversation() {
  const conversationId = useSyncExternalStore(
    subscribe,
    getSnapshot,
    getServerSnapshot
  );

  const setConversationId = useCallback((id: string) => {
    setStoredConversationId(id);
  }, []);

  return { conversationId, setConversationId };
}
