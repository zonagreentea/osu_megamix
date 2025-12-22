#!/usr/bin/env python3
"""
osu_megamix.py
A unified osu! game engine supporting:
- Standard gamemodes: osu!, Taiko, Catch, Mania
- osu!megamix: auto-mix beatmaps from user collection in real-time
"""

import os
import sys
import random
import time
from pathlib import Path

# -------------------------------
# CONFIGURATION
# -------------------------------
BEATMAP_DIR = Path.home() / "osu_beatmaps"  # user collection
SUPPORTED_MODES = ["osu", "taiko", "catch", "mania"]
MEGAMIX_MODE = "megamix"

FRAME_DELAY = 0.016  # ~60 FPS
DEBUG = True

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------
def log(msg):
    if DEBUG:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def load_beatmaps():
    if not BEATMAP_DIR.exists():
        log(f"No beatmap directory found at {BEATMAP_DIR}")
        return {}
    beatmaps = {}
    for mode in SUPPORTED_MODES:
        mode_dir = BEATMAP_DIR / mode
        if mode_dir.exists():
            beatmaps[mode] = [f for f in mode_dir.glob("*.osu")]
        else:
            beatmaps[mode] = []
    log(f"Loaded beatmaps: { {k: len(v) for k,v in beatmaps.items()} }")
    return beatmaps

def load_megamix_pool(beatmaps):
    # Flatten all beatmaps into one list for megamix
    pool = []
    for bm_list in beatmaps.values():
        pool.extend(bm_list)
    log(f"Megamix pool size: {len(pool)}")
    return pool

# -------------------------------
# GAMEPLAY CORE
# -------------------------------
class Game:
    def __init__(self):
        self.beatmaps = load_beatmaps()
        self.megamix_pool = load_megamix_pool(self.beatmaps)
        self.running = True
        self.score = 0

    def select_mode(self):
        modes = SUPPORTED_MODES + [MEGAMIX_MODE]
        print("Select gamemode:")
        for i, m in enumerate(modes, 1):
            print(f"{i}. {m}")
        choice = input("Enter number: ").strip()
        try:
            choice = int(choice) - 1
            if choice < 0 or choice >= len(modes):
                raise ValueError
            self.mode = modes[choice]
        except:
            print("Invalid choice, defaulting to osu!")
            self.mode = "osu"
        log(f"Mode selected: {self.mode}")

    def run(self):
        self.select_mode()
        if self.mode == MEGAMIX_MODE:
            self.play_megamix()
        else:
            self.play_standard(self.mode)

    def play_standard(self, mode):
        if not self.beatmaps.get(mode):
            print(f"No beatmaps available for {mode}. Exiting.")
            return
        print(f"Starting {mode} mode...")
        for bm_file in self.beatmaps[mode]:
            print(f"Playing {bm_file.name}...")
            time.sleep(1)  # placeholder for real gameplay
            self.score += random.randint(1000, 5000)
        print(f"Finished {mode} mode! Score: {self.score}")

    def play_megamix(self):
        if not self.megamix_pool:
            print("No beatmaps in megamix pool. Exiting.")
            return
        print("Starting MEGAMIX mode (real-time mix of all beatmaps)...")
        random.shuffle(self.megamix_pool)
        for bm_file in self.megamix_pool:
            print(f"Playing {bm_file.name}...")
            time.sleep(1)  # placeholder for real gameplay
            self.score += random.randint(500, 7000)
        print(f"Megamix complete! Total Score: {self.score}")

# -------------------------------
# ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    log("osu!megamix starting...")
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        print("\nGame exited by user.")
    log("osu!megamix session ended.")
