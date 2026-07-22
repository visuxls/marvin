import { SUPPRESS_BRAVE_WALLET_ERROR_SCRIPT } from "@/lib/suppress-brave-wallet-error";

describe("suppress-brave-wallet-error", () => {
  it("exports a script that filters ethereum.selectedAddress noise", () => {
    expect(SUPPRESS_BRAVE_WALLET_ERROR_SCRIPT).toContain(
      "ethereum.selectedAddress"
    );
    expect(SUPPRESS_BRAVE_WALLET_ERROR_SCRIPT).toContain("stopImmediatePropagation");
    expect(SUPPRESS_BRAVE_WALLET_ERROR_SCRIPT).toContain("addEventListener");
  });
});
