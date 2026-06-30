"use client";

import { fetchConversationMessages } from "@/lib/conversations";
import type { UIMessage } from "ai";
import { useEffect, useRef, useState } from "react";

interface UseConversationMessagesOptions {
  conversationId: string;
  setMessages: (messages: UIMessage[]) => void;
  clearError: () => void;
}

/** Load server-persisted messages when the active conversation changes. */
export function useConversationMessages({
  conversationId,
  setMessages,
  clearError,
}: UseConversationMessagesOptions) {
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const setMessagesRef = useRef(setMessages);
  const clearErrorRef = useRef(clearError);

  useEffect(() => {
    setMessagesRef.current = setMessages;
    clearErrorRef.current = clearError;
  }, [setMessages, clearError]);

  useEffect(() => {
    let cancelled = false;

    async function loadConversation() {
      setIsLoadingMessages(true);
      const stored = await fetchConversationMessages(conversationId);
      if (cancelled) {
        return;
      }
      setMessagesRef.current(stored);
      clearErrorRef.current();
      setIsLoadingMessages(false);
    }

    void loadConversation();

    return () => {
      cancelled = true;
    };
  }, [conversationId]);

  return { isLoadingMessages };
}
