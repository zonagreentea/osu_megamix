/*
osu!megamix MIC SUPPORT — NO-CONFLICT AUDIO RULES (HARD INVARIANTS)

1) Mic analysis MUST NEVER alter game audio routing.
   - Mic graph never connects to audioCtx.destination.
   - Mic graph never touches / rewires the game's playback nodes.

2) Mic MUST NOT seize ownership of any existing game AudioContext.
   - By default mic creates its OWN AudioContext (micCtx).
   - mic.stop() ONLY closes micCtx it created (never closes a foreign ctx).

3) Mic MUST NOT become the audio "source of truth" for gameplay timing.
   - Only exports level/peak metrics (0..1).
   - Intended for visuals/aux only unless you explicitly wire otherwise.

If it isn't written, it doesn't exist.
*/

export function createMic() {
  const st = {
    enabled: false,
    ready: false,
    err: null,

    micCtx: null,        // owned by mic module ONLY
    stream: null,
    source: null,
    analyser: null,
    data: null,

    _lvl: 0,
    _peak: 0,
    _hold: 0,
    _decay: 0.92,
  };

  function _compute() {
    if (!st.enabled || !st.analyser || !st.data) return;

    st.analyser.getFloatTimeDomainData(st.data);

    let sum = 0;
    let peak = 0;
    for (let i = 0; i < st.data.length; i++) {
      const v = st.data[i];
      const av = Math.abs(v);
      sum += v * v;
      if (av > peak) peak = av;
    }

    const rms = Math.sqrt(sum / st.data.length);

    // normalize-ish (keeps stable across typical mic gains)
    const lvl = Math.min(1, rms * 6.0);
    const pk  = Math.min(1, peak * 2.5);

    st._hold = Math.max(pk, st._hold * st._decay);

    st._lvl = lvl;
    st._peak = st._hold;
  }

  async function start() {
    st.err = null;
    if (st.enabled) return true;

    if (!navigator.mediaDevices?.getUserMedia) {
      st.err = new Error("Microphone not supported (no getUserMedia).");
      return false;
    }

    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) {
      st.err = new Error("WebAudio not supported (no AudioContext).");
      return false;
    }

    try {
      // user-gesture safe: created only on click
      st.micCtx = new AudioContext();

      st.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
        },
        video: false,
      });

      st.source = st.micCtx.createMediaStreamSource(st.stream);
      st.analyser = st.micCtx.createAnalyser();
      st.analyser.fftSize = 2048;
      st.analyser.smoothingTimeConstant = 0.0;

      st.data = new Float32Array(st.analyser.fftSize);

      // NO-CONFLICT RULE ENFORCEMENT:
      // connect mic -> analyser ONLY. never connect to destination.
      st.source.connect(st.analyser);

      st.enabled = true;
      st.ready = true;
      return true;
    } catch (e) {
      st.err = e;
      try { await stop(); } catch {}
      return false;
    }
  }

  async function stop() {
    st.enabled = false;

    if (st.source) {
      try { st.source.disconnect(); } catch {}
    }

    if (st.stream) {
      for (const t of st.stream.getTracks()) {
        try { t.stop(); } catch {}
      }
    }

    // micCtx is owned by this module; safe to close.
    if (st.micCtx) {
      try { await st.micCtx.close(); } catch {}
    }

    st.micCtx = null;
    st.stream = null;
    st.source = null;
    st.analyser = null;
    st.data = null;

    st.ready = false;
    st._lvl = 0;
    st._peak = 0;
    st._hold = 0;
  }

  function tick() { _compute(); }

  return {
    get enabled() { return st.enabled; },
    get ready() { return st.ready; },
    get error() { return st.err; },
    start,
    stop,
    tick,
    level: () => st._lvl,
    peak:  () => st._peak,
  };
}
