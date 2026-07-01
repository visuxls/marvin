import { describe, expect, it } from "vitest";

import { spendingCategoryAxisWidth } from "./spending-chart-axis";

describe("spendingCategoryAxisWidth", () => {
  it("widens the axis for long category names", () => {
    expect(
      spendingCategoryAxisWidth(["Food", "Transportation", "Entertainment"])
    ).toBeGreaterThan(72);
  });

  it("fits Transportation without clipping at default minimum", () => {
    const width = spendingCategoryAxisWidth(["Transportation"]);
    expect(width).toBeGreaterThanOrEqual(90);
  });
});
