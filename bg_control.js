export function applyBackgroundMods(mods) {
  // OPTIONAL: you can name these elements anything; match your DOM.
  const bgImg = document.getElementById("bgImage");
  const bgVid = document.getElementById("bgVideo");
  const dim   = document.getElementById("bgDim");

  if (bgImg) bgImg.style.display = mods.bgImage ? "" : "none";

  if (bgVid) {
    bgVid.style.display = mods.bgVideo ? "" : "none";
    // Prevent waste on mobile: pause when disabled
    if (!mods.bgVideo) {
      try { bgVid.pause(); } catch {}
    } else {
      // only play if it was meant to be playing (don’t force autoplay)
      // try { bgVid.play(); } catch {}
    }
  }

  // Dim overlay (optional)
  if (dim) {
    const a = Math.max(0, Math.min(1, Number(mods.bgDim) || 0));
    dim.style.background = `rgba(0,0,0,)`;
    dim.style.display = a > 0 ? "" : "none";
  }
}
