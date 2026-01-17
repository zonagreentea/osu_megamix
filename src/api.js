/*
MEGAMIX_API — a construct (not "just API")
- One object that owns/coordinates subsystems (mic, mix audio, hub state)
- No-conflict rules are enforced here
- Lazily instantiates subsystems (opt-in)
- Provides an event bus + stable surface for skins/engine

If it isn't written, it doesn't exist.
*/

import { createMic } from "./mic.js";
import { createMixAudio } from "./mix_audio.js";

function createBus(){
  const map = new Map();
  return {
    on(evt, fn){
      const a = map.get(evt) || [];
      a.push(fn);
      map.set(evt, a);
      return ()=>{ const b = (map.get(evt) || []).filter(x=>x!==fn); map.set(evt,b); };
    },
    emit(evt, payload){
      const a = map.get(evt) || [];
      for (const fn of a) { try { fn(payload); } catch (e) {} }
    }
  };
}

export function createMegamixAPI(){
  const bus = createBus();

  // invariants: locked, machine-readable
  const invariants = Object.freeze({
    game_audio_is_truth: true,
    mic_analysis_only: true,
    mic_never_to_destination: true,
    mic_never_closes_game_audioctx: true,
    hub_audio_opt_in_only: true,
    hub_mix_audio_is_separate_owner: true
  });

  // state
  const st = {
    mixUrl: "",
    mic: null,
    mixAudio: null,
  };

  function mixUrlFromLocation(){
    try{
      const u = new URL(location.href);
      return u.searchParams.get("mix") || "";
    }catch(e){ return ""; }
  }

  function setMixUrl(url){
    st.mixUrl = String(url || "");
    bus.emit("mix:url", st.mixUrl);
    return st.mixUrl;
  }

  // mic: reuse existing singleton if present (no duplicates)
  function ensureMic(){
    if (st.mic) return st.mic;
    st.mic = (window.MEGAMIX_MIC ||= createMic());
    bus.emit("mic:ready", true);
    return st.mic;
  }

  // mix audio: reuse existing singleton if present (no duplicates)
  function ensureMixAudio(){
    if (st.mixAudio) return st.mixAudio;
    st.mixAudio = (window.MEGAMIX_MIX_AUDIO ||= createMixAudio());
    bus.emit("mixaudio:ready", true);
    return st.mixAudio;
  }

  // public: mic control (opt-in)
  async function micOn(){
    const mic = ensureMic();
    const ok = await mic.start(); // must be called from user gesture
    bus.emit("mic:state", { enabled: ok });
    return ok;
  }
  async function micOff(){
    const mic = ensureMic();
    await mic.stop();
    bus.emit("mic:state", { enabled: false });
    return true;
  }
  function micLevel(){ return (st.mic && st.mic.enabled) ? st.mic.level() : 0; }
  function micPeak(){  return (st.mic && st.mic.enabled) ? st.mic.peak()  : 0; }

  // public: mix audio control (opt-in, separate owner)
  async function mixAudioSetSource(url){
    const a = ensureMixAudio();
    await a.setSource(String(url || ""));
    bus.emit("mixaudio:src", String(url || ""));
    return true;
  }
  async function mixAudioOn(){
    const a = ensureMixAudio();
    const src = st.mixUrl || mixUrlFromLocation();
    if (!src) { bus.emit("mixaudio:state", { enabled:false, err:"no mix url" }); return false; }
    await a.setSource(src);
    const ok = await a.start(); // must be called from user gesture
    bus.emit("mixaudio:state", { enabled: ok, err: ok ? null : (a.error ? String(a.error) : "blocked") });
    return ok;
  }
  async function mixAudioOff(){
    const a = ensureMixAudio();
    await a.stop();
    bus.emit("mixaudio:state", { enabled:false });
    return true;
  }
  function mixAudioPlaying(){ return !!(st.mixAudio && st.mixAudio.playing()); }
  function mixAudioTime(){ return st.mixAudio ? st.mixAudio.time() : 0; }

  // tick: publish globals for skins/engine (read-only by convention)
  function tick(){
    // mic metrics
    window.MEGAMIX_MIC_LEVEL = micLevel();
    window.MEGAMIX_MIC_PEAK  = micPeak();
    // mix audio time (if enabled)
    window.MEGAMIX_MIX_TIME  = mixAudioTime();
  }

  // the construct
  const api = {
    version: "MEGAMIX_API/1",
    invariants,
    bus,

    // mix url
    setMixUrl,
    get mixUrl(){ return st.mixUrl || mixUrlFromLocation(); },

    // mic
    ensureMic,
    micOn,
    micOff,
    micLevel,
    micPeak,

    // mix audio
    ensureMixAudio,
    mixAudioSetSource,
    mixAudioOn,
    mixAudioOff,
    mixAudioPlaying,
    mixAudioTime,

    // tick
    tick,
  };

  return Object.freeze(api);
}
