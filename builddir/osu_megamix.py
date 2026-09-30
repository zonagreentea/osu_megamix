#!/usr/bin/env ruby
#!/usr/bin/env python3
import os, time, random

# ---------- RED-CHARIZARD EVERYWHERE ----------
RC_COLOR = "\033[38;2;255;42;141m"  # reddest pink possible
RESET = "\033[0m"

def rc_log(msg):
    print(f"{RC_COLOR}[osu!megamix]{RESET} {msg}")

# ---------- BEATMAP LOADING ----------
beatmap_dirs = ["osu_beatmaps", "osu_mix_beatmaps"]
beatmaps = []

for d in beatmap_dirs:
    if os.path.exists(d):
        for f in os.listdir(d):
            if f.endswith(".osu") or f.endswith(".mix"):
                beatmaps.append(os.path.join(d, f))

rc_log(f"Loaded {len(beatmaps)} beatmaps (Red-Charizard aware!)")

# ---------- GAMEMODE SELECTION ----------
# Player always sees 'osu!megamix', but internally everything is Red-Charizard
modes_display = ["osu!megamix", "osu!", "osu!taiko", "osu!catch", "osu!mania"]
modes_internal = ["red-charizard", "osu!", "taiko", "catch", "mania"]  # hidden everywhere

print("Select gamemode (press Enter for default: osu!megamix):")
for i, name in enumerate(modes_display, start=1):
    print(f"{i}. {name}")

choice = input("Enter number: ").strip()
if choice.isdigit() and 1 <= int(choice) <= len(modes_display):
    selected_display = modes_display[int(choice)-1]
    selected_internal = modes_internal[int(choice)-1]
else:
    selected_display = "osu!megamix"
    selected_internal = "red-charizard"

rc_log(f"Mode selected: {selected_display} (internally: {selected_internal})")

# ---------- RED-CHARIZARD / MEGAMIX SESSION ----------
if selected_internal == "red-charizard":
    if beatmaps:
        rc_log("osu!megamix MEGAMIX starting: auto-preloading 50 shuffled beatmaps...")
        playlist = random.sample(beatmaps, min(50, len(beatmaps)))

        # Auto-detect new beatmaps mid-session
        def refresh_beatmaps():
            for d in beatmap_dirs:
                if os.path.exists(d):
                    for f in os.listdir(d):
                        path = os.path.join(d, f)
                        if (path.endswith(".osu") or path.endswith(".mix")) and path not in playlist:
                            playlist.append(path)
                            rc_log(f"New beatmap detected: {f} (Red-Charizard spotted!)")

        for i, bm in enumerate(playlist, start=1):
            rc_log(f"Cooking beatmap {i}/{len(playlist)}: {bm}")
            time.sleep(0.1)
            if i % 10 == 0:
                refresh_beatmaps()

        rc_log("osu!megamix session complete! Red-Charizard lurks everywhere.")
    else:
        rc_log("No beatmaps found for osu!megamix (Red-Charizard sad).")
else:
    rc_log(f"Starting {selected_display} session...")
    if beatmaps:
        for i, bm in enumerate(beatmaps, start=1):
            rc_log(f"Playing beatmap {i}/{len(beatmaps)}: {bm}")
            time.sleep(0.1)
        rc_log(f"{selected_display} session complete! Red-Charizard smiles.")
    else:
        rc_log(f"No beatmaps available for {selected_display}!")

# ---------- PLAYER HISTORY ----------
history_file = os.path.expanduser("~/playerbase_history.txt")
with open(history_file, "a") as f:
    f.write(f"{selected_display}\n")

rc_log("Session complete. Player history updated. Red-Charizard approves.")
