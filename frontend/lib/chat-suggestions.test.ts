import { PRESET_QUESTIONS } from "@/lib/chat-suggestions";

describe("PRESET_QUESTIONS", () => {
  it("includes multi-step finance prompts", () => {
    expect(PRESET_QUESTIONS.length).toBeGreaterThanOrEqual(9);
    expect(PRESET_QUESTIONS.map((question) => question.id)).toEqual([
      "health-check",
      "net-worth-trend",
      "concentration-risk",
      "account-breakdown",
      "cost-vs-market",
      "liquidity-stress",
      "winners-losers",
      "balance-deep-dive",
      "profile-briefing",
      "quick-snapshot",
      "market-pulse",
      "tax-loss-scan",
      "asset-location",
      "holdings-roster",
      "debt-check",
      "crypto-exposure",
      "rebalance-nudge",
      "emergency-fund",
      "spending-breakdown",
      "burn-trend",
      "runway-analysis",
      "savings-rate",
      "fixed-costs",
    ]);
  });

  it("has unique ids and prompts", () => {
    expect(new Set(PRESET_QUESTIONS.map((question) => question.id)).size).toBe(
      PRESET_QUESTIONS.length
    );
    expect(new Set(PRESET_QUESTIONS.map((question) => question.prompt)).size).toBe(
      PRESET_QUESTIONS.length
    );
  });

  it("includes titles and descriptions for each preset", () => {
    for (const question of PRESET_QUESTIONS) {
      expect(question.title.length).toBeGreaterThan(0);
      expect(question.description.length).toBeGreaterThan(0);
      expect(question.prompt.length).toBeGreaterThan(question.title.length);
    }
  });
});
