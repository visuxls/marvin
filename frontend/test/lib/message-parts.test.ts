import {
  groupMessageParts,
  isThinkingPart,
  isToolPart,
  orderMessageGroupsForDisplay,
  mergeConsecutiveAssistantMessages,
  assistantMessageHasText,
  lastTextPartIndex,
  pruneOrphanedAssistantPrefixes,
  type MessagePart,
} from "@/lib/message-parts";

describe("message-parts", () => {
  it("identifies tool parts", () => {
    expect(
      isToolPart({
        type: "tool-get_holdings",
        toolCallId: "1",
        state: "output-available",
        input: {},
        output: {},
      } as MessagePart)
    ).toBe(true);
    expect(
      isToolPart({
        type: "dynamic-tool",
        toolName: "search",
        toolCallId: "2",
        state: "input-available",
        input: {},
      } as MessagePart)
    ).toBe(true);
    expect(isToolPart({ type: "text", text: "hi" })).toBe(false);
  });

  it("identifies thinking parts", () => {
    expect(isThinkingPart({ type: "reasoning", text: "hmm" } as MessagePart)).toBe(
      true
    );
    expect(
      isThinkingPart({
        type: "tool-get_holdings",
        toolCallId: "1",
        state: "output-available",
        input: {},
        output: {},
      } as MessagePart)
    ).toBe(true);
    expect(isThinkingPart({ type: "text", text: "answer" })).toBe(false);
  });

  it("groups consecutive reasoning and tool parts", () => {
    const parts: MessagePart[] = [
      { type: "reasoning", text: "Let me check holdings." },
      {
        type: "tool-get_holdings",
        toolCallId: "1",
        state: "output-available",
        input: {},
        output: {},
      } as MessagePart,
      {
        type: "tool-get_net_worth_summary",
        toolCallId: "2",
        state: "output-available",
        input: {},
        output: {},
      } as MessagePart,
      { type: "text", text: "Your net worth is $1M." },
    ];

    const groups = groupMessageParts(parts);

    expect(groups).toHaveLength(2);
    expect(groups[0]).toEqual({
      type: "thinking",
      parts: parts.slice(0, 3),
      startIndex: 0,
    });
    expect(groups[1]).toEqual({
      type: "content",
      part: parts[3],
      index: 3,
    });
  });

  it("splits thinking groups when text appears between tools", () => {
    const parts: MessagePart[] = [
      { type: "reasoning", text: "first pass" },
      {
        type: "tool-get_holdings",
        toolCallId: "1",
        state: "output-available",
        input: {},
        output: {},
      } as MessagePart,
      { type: "text", text: "interruption" },
      {
        type: "tool-get_ticker_prices",
        toolCallId: "2",
        state: "output-available",
        input: {},
        output: {},
      } as MessagePart,
    ];

    const groups = groupMessageParts(parts);

    expect(groups).toHaveLength(3);
    expect(groups[0]?.type).toBe("thinking");
    expect(groups[1]).toEqual({ type: "content", part: parts[2], index: 2 });
    expect(groups[2]?.type).toBe("thinking");
  });

  it("returns content-only groups for user messages", () => {
    const parts: MessagePart[] = [{ type: "text", text: "Hello" }];
    expect(groupMessageParts(parts)).toEqual([
      { type: "content", part: parts[0], index: 0 },
    ]);
  });

  it("orders thinking groups before content for display", () => {
    const parts: MessagePart[] = [
      { type: "text", text: "Your allocation is concentrated." },
      { type: "reasoning", text: "Checking allocation." },
      {
        type: "tool-get_portfolio_allocation",
        toolCallId: "1",
        state: "output-available",
        input: {},
        output: {},
      } as MessagePart,
    ];

    const ordered = orderMessageGroupsForDisplay(groupMessageParts(parts));

    expect(ordered).toHaveLength(2);
    expect(ordered[0]?.type).toBe("thinking");
    expect(ordered[1]?.type).toBe("content");
  });

  it("merges consecutive assistant messages from persisted history", () => {
    const merged = mergeConsecutiveAssistantMessages([
      { id: "u1", role: "user", parts: [{ type: "text", text: "Runway?" }] },
      {
        id: "a1",
        role: "assistant",
        parts: [
          { type: "reasoning", text: "Checking burn." },
          {
            type: "tool-get_monthly_burn",
            toolCallId: "t1",
            state: "output-available",
            input: {},
            output: { has_data: true, points: [] },
          } as MessagePart,
        ],
      },
      {
        id: "a2",
        role: "assistant",
        parts: [
          { type: "reasoning", text: "Summarizing." },
          { type: "text", text: "Your runway is 7 months." },
        ],
      },
    ]);

    expect(merged).toHaveLength(2);
    expect(merged[1]?.role).toBe("assistant");
    expect(merged[1]?.id).toBe("a2");
    expect(merged[1]?.parts).toHaveLength(4);
  });

  it("does not merge consecutive assistant messages that both have text", () => {
    const merged = mergeConsecutiveAssistantMessages([
      { id: "u1", role: "user", parts: [{ type: "text", text: "Hi" }] },
      {
        id: "a1",
        role: "assistant",
        parts: [{ type: "text", text: "First answer." }],
      },
      {
        id: "a2",
        role: "assistant",
        parts: [{ type: "text", text: "Second answer." }],
      },
    ]);

    expect(merged).toHaveLength(3);
    expect(merged[1]?.id).toBe("a1");
    expect(merged[2]?.id).toBe("a2");
  });

  it("finds the last text part index", () => {
    const parts: MessagePart[] = [
      { type: "text", text: "Summary." },
      { type: "reasoning", text: "Checking." },
      {
        type: "tool-get_holdings",
        toolCallId: "1",
        state: "output-available",
        input: {},
        output: {},
      } as MessagePart,
    ];

    expect(lastTextPartIndex(parts)).toBe(0);
    expect(assistantMessageHasText({ id: "a1", role: "assistant", parts })).toBe(
      true
    );
  });

  it("prunes tool-only assistant prefixes before regenerate", () => {
    const messages = [
      { id: "u1", role: "user" as const, parts: [{ type: "text" as const, text: "Runway?" }] },
      {
        id: "a1",
        role: "assistant" as const,
        parts: [
          { type: "reasoning" as const, text: "Checking burn." },
          {
            type: "tool-get_monthly_burn",
            toolCallId: "t1",
            state: "output-available",
            input: {},
            output: {},
          } as MessagePart,
        ],
      },
      {
        id: "a2",
        role: "assistant" as const,
        parts: [{ type: "text" as const, text: "Your runway is 7 months." }],
      },
    ];

    const pruned = pruneOrphanedAssistantPrefixes(messages, "a2");

    expect(pruned).toHaveLength(2);
    expect(pruned[0]?.id).toBe("u1");
    expect(pruned[1]?.id).toBe("a2");
  });
});
