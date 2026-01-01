#!/usr/bin/env python3
import os
import time
import random
import subprocess
import atexit

from tools.megamix.cook import run_megamix_session, run_basic_session
from runtime.state.history import append_player_history
from runtime.audio.player import AudioPlayer
# STUCK AT 1: one path, one truth
SIM_HZ = 120
SIM_DT_MS = 1000 / SIM_HZ

def grade_hit(err_ms, w300=45, w100=90, w50=135):
    a = abs(int(err_ms))
    if a <= w300: return 300
    if a <= w100: return 100
    if a <= w50:  return 50
    return 0

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


def main():
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
        run_megamix_session(beatmaps, beatmap_dirs, scan_beatmaps, rc_log)
    else:
        run_basic_session(selected_display, beatmaps, rc_log)
    # ---------- PLAYER HISTORY ----------
    append_player_history(selected_display)
    rc_log("Session complete. Player history updated. Red-Charizard approves.")

if __name__ == "__main__":
    main()
