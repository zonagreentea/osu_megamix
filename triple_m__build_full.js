// triple_m.js
const MODES = ["osu","taiko","ctb","mania","mix"];
console.log("🎮 Triple M hub — choose your mode or type 'mix' for all:");
console.log(MODES.join(" | "));

let mode = prompt("Mode:")?.toLowerCase() || "mix";
if (!MODES.includes(mode)) mode = "mix";

function startMix(mode) {
    console.log(`🚀 Starting mix in mode: ${mode}`);
    let hitCount = 0;
    const totalHits = 10;
    const autoplayBurst = 5;

    function hitCircle() {
        hitCount++;
        console.log(`🎯 Hit circle ${hitCount}! (mode=${mode})`);

        // Autoplay bursts
        if (hitCount === 5) {
            console.log("🚀 Switching to autopilot temporarily…");
            let autoCount = 0;
            const autoInterval = setInterval(() => {
                autoCount++;
                console.log(`🎯 Autoplay hit circle (mode=autopilot)`);
                if (autoCount >= autoplayBurst) {
                    clearInterval(autoInterval);
                    console.log("🔄 Returning to osu!mix layer…");
                    hitCircle(); // continue main layer
                }
            }, 400);
            return;
        }

        if (hitCount < totalHits) {
            setTimeout(hitCircle, 500);
        } else {
            console.log("🏆 Done! Score: 6400");
        }
    }

    hitCircle();
}

startMix(mode);

