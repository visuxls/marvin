/**
 * Format a Unix timestamp as a compact relative time label.
 */
export function formatRelativeTime(ms: number): string {
  if (!Number.isFinite(ms) || ms <= 0) {
    return "just now";
  }

  const now = Date.now();
  const diffSeconds = Math.floor((now - ms) / 1000);

  if (diffSeconds < 10) {
    return "just now";
  }
  if (diffSeconds < 60) {
    return `${diffSeconds}s ago`;
  }

  const diffMinutes = Math.floor(diffSeconds / 60);
  if (diffMinutes < 60) {
    return `${diffMinutes}m ago`;
  }

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }

  const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) {
    return rtf.format(-diffDays, "day");
  }

  const diffWeeks = Math.floor(diffDays / 7);
  if (diffWeeks < 5) {
    return rtf.format(-diffWeeks, "week");
  }

  const diffMonths = Math.floor(diffDays / 30);
  if (diffMonths < 12) {
    return rtf.format(-diffMonths, "month");
  }

  const diffYears = Math.floor(diffDays / 365);
  return rtf.format(-diffYears, "year");
}
