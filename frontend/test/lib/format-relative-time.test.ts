import { formatRelativeTime } from "@/lib/format-relative-time";

describe("formatRelativeTime", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-06-29T12:00:00.000Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns just now for invalid or non-positive timestamps", () => {
    expect(formatRelativeTime(0)).toBe("just now");
    expect(formatRelativeTime(-1)).toBe("just now");
    expect(formatRelativeTime(Number.NaN)).toBe("just now");
  });

  it("returns just now for timestamps within 10 seconds", () => {
    const now = Date.now();
    expect(formatRelativeTime(now - 5_000)).toBe("just now");
  });

  it("formats seconds ago", () => {
    const now = Date.now();
    expect(formatRelativeTime(now - 30_000)).toBe("30s ago");
  });

  it("formats minutes ago", () => {
    const now = Date.now();
    expect(formatRelativeTime(now - 5 * 60_000)).toBe("5m ago");
  });

  it("formats hours ago", () => {
    const now = Date.now();
    expect(formatRelativeTime(now - 3 * 60 * 60_000)).toBe("3h ago");
  });

  it("formats days with Intl.RelativeTimeFormat", () => {
    const now = Date.now();
    expect(formatRelativeTime(now - 2 * 24 * 60 * 60_000)).toBe("2 days ago");
  });

  it("formats weeks with Intl.RelativeTimeFormat", () => {
    const now = Date.now();
    expect(formatRelativeTime(now - 14 * 24 * 60 * 60_000)).toBe("2 weeks ago");
  });

  it("formats months with Intl.RelativeTimeFormat", () => {
    const now = Date.now();
    expect(formatRelativeTime(now - 60 * 24 * 60 * 60_000)).toBe("2 months ago");
  });

  it("formats years with Intl.RelativeTimeFormat", () => {
    const now = Date.now();
    expect(formatRelativeTime(now - 400 * 24 * 60 * 60_000)).toBe("last year");
  });
});
