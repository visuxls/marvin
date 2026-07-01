import { describe, expect, it } from "vitest";

import { netWorthYAxisDomain } from "./chart-axis-domain";

describe("netWorthYAxisDomain", () => {
  it("pads a tight range instead of starting at zero", () => {
    const [min, max] = netWorthYAxisDomain([98_000, 99_500, 100_000]);
    expect(min).toBeGreaterThan(90_000);
    expect(max).toBeLessThan(105_000);
    expect(min).toBeLessThan(98_000);
    expect(max).toBeGreaterThan(100_000);
  });

  it("adds cushion when all values are identical", () => {
    const [min, max] = netWorthYAxisDomain([250_000, 250_000, 250_000]);
    expect(min).toBeLessThan(250_000);
    expect(max).toBeGreaterThan(250_000);
  });
});
