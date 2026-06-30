import {
  groupMessageParts,
  isThinkingPart,
  isToolPart,
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
});
