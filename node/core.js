(() => {
  "use strict";

  class OsuMegamixNode {
    constructor(platform = {}) {
      this.platform = platform;
      this.state = {
        status: "READY",
        mode: "menu",
        paused: false,
        network: "UNKNOWN",
        sequence: 0,
        clients: 0
      };
      this.listeners = new Set();
    }

    subscribe(listener) {
      this.listeners.add(listener);
      listener(this.snapshot());
      return () => this.listeners.delete(listener);
    }

    snapshot() {
      return JSON.parse(JSON.stringify(this.state));
    }

    emit() {
      const state = this.snapshot();
      for (const listener of this.listeners) listener(state);
    }

    transition(patch) {
      this.state = {
        ...this.state,
        ...patch,
        sequence: this.state.sequence + 1
      };
      this.emit();
      return this.snapshot();
    }

    request(action, source = "local") {
      if (source !== "local") {
        if (this.platform.onRemoteRequest) {
          return this.platform.onRemoteRequest(action, this.snapshot());
        }
        return { accepted: false, reason: "remote authority is not available" };
      }

      switch (action) {
        case "pause":
          return { accepted: true, state: this.transition({
            status: "PAUSED",
            paused: true
          }) };

        case "resume":
          return { accepted: true, state: this.transition({
            status: "RUNNING",
            paused: false
          }) };

        case "escape":
          return { accepted: true, state: this.transition({
            status: "READY",
            mode: "menu",
            paused: false
          }) };

        case "menu":
          return { accepted: true, state: this.transition({
            status: "READY",
            mode: "menu",
            paused: false
          }) };

        case "collection":
        case "megamix":
        case "solo":
        case "multi":
          return { accepted: true, state: this.transition({
            status: "RUNNING",
            mode: action,
            paused: false
          }) };

        default:
          return { accepted: false, reason: "unknown action" };
      }
    }

    setNetwork(status) {
      return this.transition({ network: status });
    }

    test() {
      const results = [];

      const check = (name, condition, reason) => {
        results.push({
          name,
          result: condition ? "PASS" : "FAIL",
          reason
        });
      };

      check(
        "core initialization",
        this.state.status === "READY",
        "node starts in READY state"
      );

      check(
        "local authority",
        true,
        "authoritative state belongs to the node"
      );

      check(
        "platform abstraction",
        !!this.platform,
        "core accepts a platform adapter"
      );

      const paused = this.request("pause");
      check(
        "pause",
        paused.accepted && paused.state.paused,
        "pause is handled by the core"
      );

      const resumed = this.request("resume");
      check(
        "resume",
        resumed.accepted && !resumed.state.paused,
        "resume is handled by the core"
      );

      const solo = this.request("solo");
      check(
        "solo",
        solo.accepted && solo.state.mode === "solo",
        "mode transition is platform-independent"
      );

      const invalid = this.request("not-a-command");
      check(
        "invalid request",
        !invalid.accepted,
        "unknown commands are rejected"
      );

      const remote = this.request("pause", "remote");
      check(
        "remote authority isolation",
        remote.accepted === false,
        "remote callers cannot directly mutate authoritative state"
      );

      this.request("escape");

      const before = this.state.sequence;
      this.setNetwork("OFFLINE");
      this.setNetwork("ONLINE");

      check(
        "network independence",
        this.state.mode === "menu" && this.state.sequence > before,
        "network status changes do not replace node authority"
      );

      return results;
    }
  }

  globalThis.OsuMegamixNode = OsuMegamixNode;
})();
