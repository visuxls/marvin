/**
 * Brave iOS injects wallet cleanup that does
 * `window.ethereum.selectedAddress = undefined` on non-HTTPS pages.
 * When `window.ethereum` is missing (HTTP LAN IP), that throws and Next.js
 * dev overlay treats it as an app crash — blocking the whole UI.
 *
 * Capture-phase listener must run before Next's error overlay attaches.
 * See: https://github.com/brave/brave-ios/issues/6656
 */
export const SUPPRESS_BRAVE_WALLET_ERROR_SCRIPT = `(function () {
  function isBraveWalletNoise(value) {
    return typeof value === "string" && value.indexOf("ethereum.selectedAddress") !== -1;
  }
  window.addEventListener(
    "error",
    function (event) {
      if (isBraveWalletNoise(event.message)) {
        event.preventDefault();
        event.stopImmediatePropagation();
      }
    },
    true
  );
  window.addEventListener(
    "unhandledrejection",
    function (event) {
      var reason = event.reason;
      var message =
        typeof reason === "string"
          ? reason
          : reason && typeof reason.message === "string"
            ? reason.message
            : String(reason || "");
      if (isBraveWalletNoise(message)) {
        event.preventDefault();
        event.stopImmediatePropagation();
      }
    },
    true
  );
})();`;
