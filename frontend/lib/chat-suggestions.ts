/** Multi-step preset prompts for the empty-state suggestion carousel. */
export type PresetQuestion = {
  id: string;
  title: string;
  description: string;
  prompt: string;
};

export const PRESET_QUESTIONS: readonly PresetQuestion[] = [
  {
    id: "health-check",
    title: "Financial health check",
    description: "Net worth, allocation, cash flow, and liquidity in one view",
    prompt:
      "Give me a complete financial health check: net worth at current market prices, portfolio allocation, unrealized gains, and how my cash compares to invested assets. If transaction data is available, add recent income versus spending, savings rate, and runway from actual burn — otherwise note that cash-flow data is missing. Call out anything that looks off.",
  },
  {
    id: "net-worth-trend",
    title: "Am I growing?",
    description: "Net worth trend and what changed over time",
    prompt:
      "How has my net worth trended over time? Show the history, summarize the change, and explain what's driving it using my balances and holdings.",
  },
  {
    id: "concentration-risk",
    title: "Concentration & risk",
    description: "Largest positions and portfolio weightings",
    prompt:
      "Value my holdings at market prices, show portfolio allocation by symbol, and highlight any large concentrations or outsized unrealized gains or losses I should know about.",
  },
  {
    id: "account-breakdown",
    title: "Where is my money?",
    description: "Net worth split across every account",
    prompt:
      "Break down my net worth by account, list my latest cash balances, and summarize my investment holdings in each brokerage. Tell me which accounts hold the most.",
  },
  {
    id: "cost-vs-market",
    title: "Book vs. market value",
    description: "Cost basis net worth against live market prices",
    prompt:
      "Compare my net worth at cost basis versus current market prices. Quantify the total gap, rank my holdings by unrealized gain or loss, and explain which positions are driving most of the difference.",
  },
  {
    id: "liquidity-stress",
    title: "Liquidity stress test",
    description: "Cash buffers, liquid assets, and runway",
    prompt:
      "Run a liquidity stress test: pull my latest cash balances by account, summarize liquid versus invested assets, and assess whether my cash reserves look adequate relative to total net worth. If transaction data is available, use actual monthly burn to estimate runway months at current spending and say whether that buffer feels thin or comfortable — otherwise note that burn-based runway isn't available. Flag any accounts that seem light on cash.",
  },
  {
    id: "winners-losers",
    title: "Winners & losers",
    description: "Best and worst performers with allocation context",
    prompt:
      "Identify my biggest portfolio winners and losers at market value, show current allocation weights by symbol, and call out any positions that are both large in weight and sitting on heavy unrealized gains or losses.",
  },
  {
    id: "balance-deep-dive",
    title: "Balance history audit",
    description: "Month-over-month swings across every account",
    prompt:
      "Pull balance history for every account and my net worth over time. Highlight the largest month-over-month swings, name which accounts moved the most, and say whether the overall trend is improving or deteriorating.",
  },
  {
    id: "profile-briefing",
    title: "Personalized CFO briefing",
    description:
      "Full balance-sheet review tied to your goals, risks, and next steps",
    prompt:
      "Read my profile first, then deliver a comprehensive personalized CFO briefing using all relevant tools. Structure it as follows:\n\n" +
      "1. **Executive summary** — One tight paragraph: who I am (life stage, income situation, priorities from my profile), total net worth at current market prices, and the single most important takeaway for me right now.\n\n" +
      "2. **Balance sheet snapshot** — Net worth at market prices and at cost basis; quantify the book-to-market gap. Break down cash vs. invested assets and flag any credit balances or liabilities.\n\n" +
      "3. **Trend & momentum** — Net worth over time and balance history highlights: is the trajectory improving or deteriorating? Call out the largest month-over-month swings and which accounts drove them.\n\n" +
      "4. **Liquidity & runway** — Liquid vs. invested split, cash by account, and whether reserves look adequate for my situation (employment status, dependents, major expenses from my profile). Use transaction history for monthly burn, spending breakdown, and runway when available; only fall back to profile expense notes if transaction data is missing.\n\n" +
      "5. **Portfolio health** — Allocation by symbol at market prices, top winners and losers, total unrealized gain/loss, and any dangerous concentrations (large weight + heavy gain or loss).\n\n" +
      "6. **Account map** — Where my money lives: net worth by account, latest balances, and holdings per brokerage. Name which accounts matter most.\n\n" +
      "7. **Strategic read** — Connect the numbers to my stated goals, risk tolerance, timeline, and near-term priorities. Be opinionated: what's working, what's exposed, and what I'd regret ignoring.\n\n" +
      "8. **Risks & watchouts** — Proactively flag concentration, liquidity gaps, deteriorating trends, or anything unusual — even if I didn't ask.\n\n" +
      "9. **Next steps** — Three to five concrete, prioritized actions tied to my profile (not generic advice). Include what to do first and why.\n\n" +
      "Use actual figures throughout. Lead with insight, not raw data dumps.",
  },
  {
    id: "quick-snapshot",
    title: "Quick snapshot",
    description: "Net worth and cash in under a minute",
    prompt:
      "Give me a quick financial snapshot: total net worth at current market prices, how much is cash versus invested, and which three accounts hold the most. Keep it brief — no deep dives unless something stands out.",
  },
  {
    id: "market-pulse",
    title: "Live market pulse",
    description: "Current prices and book-to-market on every holding",
    prompt:
      "Pull live prices for all my holdings and value the portfolio at market. For each position, show quantity, average cost, current price, market value, and unrealized gain or loss. Summarize total unrealized P&L and flag any position where market value diverges sharply from cost basis.",
  },
  {
    id: "tax-loss-scan",
    title: "Tax-loss scan",
    description: "Underwater positions that may warrant a harvest review",
    prompt:
      "Scan my portfolio for tax-loss harvesting candidates. List every holding with an unrealized loss, sorted by largest loss first. For each, show cost basis, market value, loss amount, and portfolio weight. Note wash-sale or holding-period considerations only at a high level — I want a prioritization list, not tax advice.",
  },
  {
    id: "asset-location",
    title: "Retirement vs. taxable",
    description: "How wealth is split across account types",
    prompt:
      "Summarize my liquidity breakdown: cash, taxable investments, retirement accounts, crypto, and credit balances. Show dollar amounts and percentage of total net worth for each bucket. Call out if I'm heavily skewed toward one category relative to a typical allocation for my life stage (use my profile for context).",
  },
  {
    id: "holdings-roster",
    title: "Full holdings roster",
    description: "Every position with quantity, cost, and market value",
    prompt:
      "List every investment holding I have: symbol, account, quantity, average cost per share, total cost basis, current market price, market value, and unrealized gain or loss. Present it as a clear table-style summary, then note total invested at cost versus total at market.",
  },
  {
    id: "debt-check",
    title: "Credit & liabilities",
    description: "Outstanding credit balances and how they affect net worth",
    prompt:
      "Focus on debt and credit: list all accounts with credit-card or loan types, show latest balances, and quantify total liabilities. Net them against my assets to show how much they drag on net worth. Flag any account with an unusually large balance from balance history if visible.",
  },
  {
    id: "crypto-exposure",
    title: "Crypto exposure",
    description: "Bitcoin, ether, and crypto weight in the portfolio",
    prompt:
      "Assess my cryptocurrency exposure: identify crypto holdings and accounts, value them at current market prices, and show what percentage of total net worth and of invested assets is in crypto. Compare cost basis to market value and flag if concentration in crypto looks high.",
  },
  {
    id: "rebalance-nudge",
    title: "Rebalance nudge",
    description: "Overweight positions and trim candidates",
    prompt:
      "Show my portfolio allocation by symbol at market prices. Identify positions that are overweight (roughly above 15–20% of invested assets or clearly dominant) and underweight tail holdings. Suggest which symbols I'd trim or diversify away from first — opinionated but based only on current weights, not invented target allocations.",
  },
  {
    id: "emergency-fund",
    title: "Emergency fund check",
    description: "Cash reserves vs. actual or estimated monthly expenses",
    prompt:
      "Read my profile, then evaluate my emergency fund: total liquid cash across checking and savings accounts and how many months of expenses that covers. Prefer actual average monthly spending from transaction history when available; otherwise use expense or income notes from my profile. Say whether the reserve looks thin, adequate, or strong. Be specific with dollar amounts.",
  },
  {
    id: "spending-breakdown",
    title: "Where does my money go?",
    description: "Category spending, income, and what dominates outflows",
    prompt:
      "Analyze my spending over the last three months from transaction history. Break down outflows by category with dollar amounts and percentage weights, show total income in the same period, and call out the top three categories driving my spending. Flag any category that looks unusually high or has spiked recently compared to earlier months.",
  },
  {
    id: "burn-trend",
    title: "Spending momentum",
    description: "Month-by-month income, spending, and net burn",
    prompt:
      "Pull my monthly burn trend for the last six months. For each month show income, total spending, and net burn. Summarize whether spending is rising, falling, or flat, identify the best and worst months for cash flow, and explain what's driving any changes you see.",
  },
  {
    id: "runway-analysis",
    title: "Real runway",
    description: "Months of runway from liquid cash and actual spending",
    prompt:
      "Calculate my runway using real transaction history: average monthly burn from recent months and total liquid cash in checking and savings. Show how many months I can cover at current spending, read my profile to assess whether that runway fits my employment situation and goals, and flag if reserves look tight or comfortable.",
  },
  {
    id: "savings-rate",
    title: "Living within my means?",
    description: "Income vs. spending and monthly savings rate",
    prompt:
      "Using my transaction history, compare total income to total spending over the last three months. Calculate my effective savings rate (net surplus or deficit as a percent of income), show the month-by-month breakdown, and read my profile to assess whether this pace aligns with my stated goals. Be direct about whether I'm ahead or behind.",
  },
  {
    id: "fixed-costs",
    title: "Fixed cost audit",
    description: "Recurring bills and their share of income",
    prompt:
      "Review my transactions to identify recurring fixed costs — rent, debt payments, subscriptions, memberships, transit passes, and similar repeating charges. Estimate total monthly fixed obligations, list each line item with its amount, and calculate what percentage of my average monthly income they consume. Highlight anything that looks trimmable without major lifestyle change.",
  },
] as const;
