/*
Hub-owned mix audio player (NO-CONFLICT)
- Uses HTMLAudioElement for maximum Safari compatibility.
- Does NOT touch any existing game audio graph.
- Only becomes the mix audio truth if you enable it.
*/

export function createMixAudio() {
  const st = {
    enabled: false,
    el: null,
    src: "",
    err: null,
    volume: 1.0,
  };

  function _ensure() {
    if (st.el) return;
    const a = new Audio();
    a.preload = "auto";
    a.crossOrigin = "anonymous";
    a.loop = false;
    a.volume = st.volume;
    st.el = a;
  }

  async function setSource(url) {
    st.err = null;
    st.src = url || "";
    _ensure();
    st.el.pause();
    st.el.src = st.src;
    st.el.load();
    return true;
  }

  async function start() {
    st.err = null;
    if (!st.src) { st.err = new Error("No mix audio source set."); return false; }
    _ensure();
    try {
      await st.el.play(); // requires user gesture in Safari; call from click
      st.enabled = true;
      return true;
    } catch (e) {
      st.err = e;
      st.enabled = false;
      return false;
    }
  }

  async function stop() {
    if (!st.el) return;
    st.enabled = false;
    try { st.el.pause(); } catch {}
  }

  function setVolume(v) {
    st.volume = Math.max(0, Math.min(1, Number(v)));
    if (st.el) st.el.volume = st.volume;
  }

  function time() { return st.el ? st.el.currentTime : 0; }
  function playing() { return !!(st.el && !st.el.paused); }

  return {
    get enabled(){ return st.enabled; },
    get error(){ return st.err; },
    setSource,
    start,
    stop,
    setVolume,
    time,
    playing,
  };
}
