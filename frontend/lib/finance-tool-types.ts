export type AllocationSlice = {
  symbol: string;
  market_value: unknown;
  weight_pct: unknown;
};

export type PortfolioAllocationOutput = {
  total_market_value: unknown;
  slices: AllocationSlice[];
  holdings_missing_prices: number;
};

export type NetWorthHistoryPoint = {
  date: string;
  cash_and_credit_total: unknown;
  investment_cost_basis_total: unknown;
  net_worth_total: unknown;
};

export type NetWorthHistoryOutput = {
  points: NetWorthHistoryPoint[];
  investment_values_are_current_snapshot?: boolean;
};

export type MonthlyBurnPoint = {
  month: string;
  spending: unknown;
  income: unknown;
  net_burn: unknown;
};

export type MonthlyBurnOutput = {
  points: MonthlyBurnPoint[];
  average_monthly_burn: unknown;
  has_data: boolean;
};

export type CategorySpending = {
  category: string;
  amount: unknown;
  transaction_count: number;
  weight_pct: unknown;
};

export type SpendingBreakdownOutput = {
  period_start: string;
  period_end: string;
  total_spending: unknown;
  total_income: unknown;
  categories: CategorySpending[];
  has_data: boolean;
};

export type ChartableToolKind =
  | "portfolio_allocation"
  | "net_worth_over_time"
  | "monthly_burn"
  | "spending_breakdown";

export type ChartableTool = {
  toolCallId: string;
  toolName: string;
  kind: ChartableToolKind;
  output: unknown;
};
