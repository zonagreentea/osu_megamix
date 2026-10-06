(() => {
  "use strict";

  const platform = {
    name: "html",

    input: {
      onKey(callback) {
        window.addEventListener("keydown", event => callback(event));
      }
    },

    storage: {
      get(key) {
        try { return localStorage.getItem(key); }
        catch { return null; }
      },

      set(key, value) {
        try {
          localStorage.setItem(key, value);
          return true;
        } catch {
          return false;
        }
      }
    },

    network: {
      online() {
        return navigator.onLine;
      },

      onChange(callback) {
        window.addEventListener("online", () => callback("ONLINE"));
        window.addEventListener("offline", () => callback("OFFLINE"));
      }
    },

    clock: {
      now() {
        return Date.now();
      }
    },

    output: {
      log(...args) {
        console.log("[osu_megamix node]", ...args);
      }
    },

    onRemoteRequest() {
      return {
        accepted: false,
        reason: "HTML wrapper does not grant remote authority"
      };
    }
  };

  globalThis.OsuMegamixHTMLPlatform = platform;
})();
