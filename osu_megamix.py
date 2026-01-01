#!/usr/bin/env python3
import os
import time
import random
import subprocess
import atexit

# STUCK AT 1: one path, one truth
SIM_HZ = 120
SIM_DT_MS = 1000 / SIM_HZ

def grade_hit(err_ms, w300=45, w100=90, w50=135):
    a = abs(int(err_ms))
    if a <= w300: return 300
    if a <= w100: return 100
    if a <= w50:  return 50
    return 0

class AudioPlayer:
    def __init__(self, path):
        self.path = path
        self.proc = None
        self.t0 = None

    def start(self):
        if not self.path:
            return False
        p = os.path.abspath(self.path)
        if not os.path.exists(p):
            return False

        # Hard truth: macOS afplay
        self.proc = subprocess.Popen(
            ["/usr/bin/afplay", "-q", p],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.t0 = time.perf_counter()
        return True

    def stop(self):
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
            self.proc = None

    def now_ms(self):
        if self.t0 is None:
            return int(time.perf_counter() * 1000)
        return int((time.perf_counter() - self.t0) * 1000)

class SimpleReplay:
    def __init__(self, path="last_replay.omxr"):
        self.path = path
        self.f = open(self.path, "w", encoding="utf-8")
        self.f.write("OMXR1\n")  # magic/version
        self.last = None
        atexit.register(self.close)

    def write(self, sim_t, mask, x, y):
        cur = (sim_t, mask, x, y)
        if cur == self.last:
            return
        self.f.write(f"{sim_t},{mask},{x},{y}\n")
        self.last = cur

    def close(self):
        try:
            if self.f:
                self.f.close()
        except Exception:
            pass

# ---------- RED-CHARIZARD EVERYWHERE ----------
RC_COLOR = "\033[38;2;255;42;141m"  # reddest pink possible
RESET = "\033[0m"

def rc_log(msg):
    print(f"{RC_COLOR}[osu!megamix]{RESET} {msg}")

# ---------- BEATMAP LOADING ----------
beatmap_dirs = ["osu_beatmaps", "osu_mix_beatmaps", "beatmaps"]  # include your repo default too

def scan_beatmaps(dirs):
    out = []
    seen = set()
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith(".osu") or f.endswith(".mix"):
                    path = os.path.join(root, f)
                    if path not in seen:
                        seen.add(path)
                        out.append(path)
    return out

beatmaps = scan_beatmaps(beatmap_dirs)
rc_log(f"Loaded {len(beatmaps)} beatmaps (Red-Charizard aware!)")

# ---------- GAMEMODE SELECTION ----------
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

# ---------- SESSION ----------
if selected_internal == "red-charizard":
    if beatmaps:
        rc_log("osu!megamix MEGAMIX starting: auto-preloading 50 shuffled beatmaps...")
        playlist = random.sample(beatmaps, min(50, len(beatmaps)))

        def refresh_beatmaps():
            nonlocal_beatmaps = scan_beatmaps(beatmap_dirs)
            # add new ones to playlist (keep uniqueness)
            have = set(playlist)
            added = 0
            for p in nonlocal_beatmaps:
                if p not in have:
                    playlist.append(p)
                    have.add(p)
                    added += 1
                    rc_log(f"New beatmap detected: {os.path.basename(p)} (Red-Charizard spotted!)")
            return added

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
with open(history_file, "a", encoding="utf-8") as f:
    f.write(f"{selected_display}\n")

rc_log("Session complete. Player history updated. Red-Charizard approves.")
