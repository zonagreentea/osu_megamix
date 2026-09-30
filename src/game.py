import datetime
import time

def run(enable_npc=False, safe_mode=False, no_audio=False, mode="osu!mix", log_file=None, autopilot_duration=3):
    """
    Megamix runner with temporary autopilot.

    Parameters:
    - enable_npc: bool, NPCs auto-play
    - safe_mode: bool
    - no_audio: bool
    - mode: str, starting mode ("osu!mix")
    - log_file: str, optional
    - autopilot_duration: int, seconds to run temporary autopilot before returning to mix
    """
    if log_file is None:
        log_file = f"logs/megamix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    print(f"🎮 Starting {mode}… NPCs: {enable_npc}, Safe: {safe_mode}, Audio: {not no_audio}")
    print(f"📝 Logging to {log_file}")

    # Start mix layer
    current_mode = mode
    for i in range(1, 6):
        print(f"🎯 Hit circle {i}! (mode={current_mode})")
        time.sleep(0.3 if not enable_npc else 0.15)

    # Temporary autopilot
    print("🚀 Switching to autopilot temporarily…")
    current_mode = "autopilot"
    start = time.time()
    while time.time() - start < autopilot_duration:
        print(f"🎯 Autoplay hit circle (mode={current_mode})")
        time.sleep(0.3 if not enable_npc else 0.15)

    # Return to mix layer
    print("🔄 Returning to osu!mix layer…")
    current_mode = mode
    for i in range(6, 11):
        print(f"🎯 Hit circle {i}! (mode={current_mode})")
        time.sleep(0.3 if not enable_npc else 0.15)

    print("🏆 Done! Score: 6400")

