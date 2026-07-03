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
  const modelRef = useRef(model);
  useEffect(() => {
    modelRef.current = model;
  }, [model]);

  // useChat only recreates its Chat instance when `id` changes, not when transport
  // changes. Read the selected model from a ref so each request uses the current
  // picker value instead of the model that was active on first mount.
  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: chatApiUrl(),
        body: () => ({
          model: modelRef.current || undefined,
        }),
      }),
    []
  );

  const chat = useChat({
    transport,
    id: conversationId,
    // Batch stream updates so Streamdown/markdown re-renders do not exceed React's
    // nested update limit on long tool-heavy replies (see AI SDK troubleshooting).
    experimental_throttle: 50,
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
