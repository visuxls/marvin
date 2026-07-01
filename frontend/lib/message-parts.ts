import type { DynamicToolUIPart, ToolUIPart, UIMessage } from "ai";

export type MessagePart = UIMessage["parts"][number];

export type ThinkingPartGroup = {
  type: "thinking";
  parts: MessagePart[];
  startIndex: number;
};

export type ContentPartGroup = {
  type: "content";
  part: MessagePart;
  index: number;
};

export type MessagePartGroup = ThinkingPartGroup | ContentPartGroup;

export function isToolPart(
  part: MessagePart
): part is ToolUIPart | DynamicToolUIPart {
  return part.type === "dynamic-tool" || part.type.startsWith("tool-");
}

export function isThinkingPart(part: MessagePart): boolean {
  return part.type === "reasoning" || isToolPart(part);
}

export function assistantMessageHasText(message: UIMessage): boolean {
  return message.parts.some((part) => part.type === "text");
}

/**
 * Index of the last text part in a message, or -1 when none exist.
 */
export function lastTextPartIndex(parts: MessagePart[]): number {
  for (let index = parts.length - 1; index >= 0; index--) {
    if (parts[index]?.type === "text") {
      return index;
    }
  }
  return -1;
}

/**
 * Drop tool-only assistant prefixes before regenerating a later assistant message.
 */
export function pruneOrphanedAssistantPrefixes(
  messages: UIMessage[],
  messageId: string
): UIMessage[] {
  const index = messages.findIndex((message) => message.id === messageId);
  if (index <= 0) {
    return messages;
  }

  let pruneFrom = index;
  while (
    pruneFrom > 0 &&
    messages[pruneFrom - 1]?.role === "assistant" &&
    !assistantMessageHasText(messages[pruneFrom - 1]!)
  ) {
    pruneFrom--;
  }

  if (pruneFrom === index) {
    return messages;
  }

  return [...messages.slice(0, pruneFrom), ...messages.slice(index)];
}

/**
 * Group consecutive reasoning and tool parts into thinking blocks.
 *
 * Args:
 *   parts: Ordered UI message parts from a single message.
 *
 * Returns:
 *   Thinking groups followed by content parts in original order.
 */
export function groupMessageParts(parts: MessagePart[]): MessagePartGroup[] {
  const groups: MessagePartGroup[] = [];
  let thinkingParts: MessagePart[] = [];
  let thinkingStartIndex = 0;

  const flushThinking = (nextIndex: number) => {
    if (thinkingParts.length === 0) {
      return;
    }
    groups.push({
      type: "thinking",
      parts: thinkingParts,
      startIndex: thinkingStartIndex,
    });
    thinkingParts = [];
    thinkingStartIndex = nextIndex;
  };

  parts.forEach((part, index) => {
    if (isThinkingPart(part)) {
      if (thinkingParts.length === 0) {
        thinkingStartIndex = index;
      }
      thinkingParts.push(part);
      return;
    }

    flushThinking(index);
    groups.push({ type: "content", part, index });
  });

  flushThinking(parts.length);
  return groups;
}

/**
 * Order message groups for display: thinking blocks, then text content.
 *
 * Persisted messages may store parts as text-before-tools; live streams usually
 * emit tools first. Canonical display order matches the live-chat layout.
 */
export function orderMessageGroupsForDisplay(
  groups: MessagePartGroup[]
): MessagePartGroup[] {
  const thinking = groups.filter((group) => group.type === "thinking");
  const content = groups.filter((group) => group.type === "content");
  return [...thinking, ...content];
}

/**
 * Merge consecutive assistant UI messages into one display turn.
 *
 * Persisted history from ``VercelAIAdapter.dump_messages`` often splits tool
 * steps and the final answer into separate assistant messages; live streaming
 * keeps a single growing message.
 */
export function mergeConsecutiveAssistantMessages(
  messages: UIMessage[]
): UIMessage[] {
  const merged: UIMessage[] = [];

  for (const message of messages) {
    if (message.role !== "assistant") {
      merged.push(message);
      continue;
    }

    const previous = merged[merged.length - 1];
    if (
      previous?.role === "assistant" &&
      !assistantMessageHasText(previous)
    ) {
      merged[merged.length - 1] = {
        ...message,
        parts: [...previous.parts, ...message.parts],
      };
      continue;
    }

    merged.push(message);
  }

  return merged;
}
