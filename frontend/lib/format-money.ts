const moneyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const compactMoneyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 1,
});

/**
 * Format a number as USD for chart labels and tooltips.
 */
export function formatMoney(value: number, compact = false): string {
  const formatter = compact ? compactMoneyFormatter : moneyFormatter;
  return formatter.format(value);
}

/**
 * Format a percentage for chart labels.
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}
