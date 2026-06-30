"use client";

import { chatApiUrl } from "@/lib/marvin-api";
import { useChat } from "@ai-sdk/react";
import {
  DefaultChatTransport,
  lastAssistantMessageIsCompleteWithApprovalResponses,
} from "ai";
import { useEffect, useMemo, useRef } from "react";

interface UseMarvinChatOptions {
  conversationId: string;
  model: string;
  onChatComplete?: () => void;
}

/** Wire useChat to the Marvin backend with model selection and completion callbacks. */
export function useMarvinChat({
  conversationId,
  model,
  onChatComplete,
}: UseMarvinChatOptions) {
  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: chatApiUrl(),
        body: () => ({
          model: model || undefined,
        }),
      }),
    [model]
  );

  const chat = useChat({
    transport,
    id: conversationId,
    sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithApprovalResponses,
  });

  const onChatCompleteRef = useRef(onChatComplete);

  useEffect(() => {
    onChatCompleteRef.current = onChatComplete;
  }, [onChatComplete]);

  const previousStatusRef = useRef(chat.status);
  useEffect(() => {
    const wasBusy =
      previousStatusRef.current === "submitted" ||
      previousStatusRef.current === "streaming";
    const isReady = chat.status === "ready";
    if (wasBusy && isReady) {
      onChatCompleteRef.current?.();
    }
    previousStatusRef.current = chat.status;
  }, [chat.status]);

  const isBusy =
    chat.status === "submitted" || chat.status === "streaming";

  return { ...chat, isBusy };
}
