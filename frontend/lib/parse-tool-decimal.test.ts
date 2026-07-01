import { describe, expect, it } from "vitest";

import { parseToolDecimal } from "./parse-tool-decimal";

describe("parseToolDecimal", () => {
  it("parses finite numbers", () => {
    expect(parseToolDecimal(42.5)).toBe(42.5);
  });

  it("parses decimal strings from pydantic", () => {
    expect(parseToolDecimal("31000.00")).toBe(31000);
  });

  it("returns null for invalid values", () => {
    expect(parseToolDecimal("")).toBeNull();
    expect(parseToolDecimal("not-a-number")).toBeNull();
    expect(parseToolDecimal(null)).toBeNull();
    expect(parseToolDecimal(Number.NaN)).toBeNull();
  });
});
