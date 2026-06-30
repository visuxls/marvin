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
