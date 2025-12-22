#!/usr/bin/env python3
import os, platform, random, time, tarfile
from pathlib import Path
from datetime import datetime

# ---------------- Configuration ----------------
SUPPORTED_EXTENSIONS = (".osu", ".mix")
POOL_SIZE = 20  # Number of maps to queue for live MEGAMIX
PLAYER_HISTORY = Path.home() / "playerbase_history.txt"
BACKUP_DIR = Path.home() / "osu_megamix_backups"
EXTRA_COLLECTION = Path.home() / "osu_extra_collection"

# Default beatmap locations per platform
OSU_LOCATIONS = {
    "windows": [
        os.path.expandvars(r"%APPDATA%\osu\Songs"),
        os.path.expandvars(r"%LOCALAPPDATA%\osu!\Songs")
    ],
    "darwin": [
        Path.home() / "Library/Application Support/osu/Songs",
        Path.home() / "Library/Application Support/osu!/Songs"
    ],
    "linux": [
        Path.home() / ".local/share/osu/Songs",
        Path.home() / ".local/share/osu!/Songs"
    ]
}

# ---------------- Helper Functions ----------------
def get_platform():
    plat = platform.system().lower()
    if "darwin" in plat: return "darwin"
    if "windows" in plat: return "windows"
    return "linux"

def scan_beatmaps():
    beatmaps = []
    plat = get_platform()
    locations = OSU_LOCATIONS.get(plat, []) + ([EXTRA_COLLECTION] if EXTRA_COLLECTION.exists() else [])
    for loc in locations:
        if not os.path.exists(loc): continue
        for root, dirs, files in os.walk(loc):
            for f in files:
                if f.endswith(SUPPORTED_EXTENSIONS):
                    beatmaps.append(Path(root) / f)
    return beatmaps

def backup_assets():
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"assets_backup_{timestamp}.tar.gz"
    with tarfile.open(backup_file, "w:gz") as tar:
        for map_file in scan_beatmaps():
            tar.add(map_file, arcname=map_file.name)
    print(f"[osu!megamix] Backup completed: {backup_file}")

def watch_beatmaps(interval=5):
    known = set()
    while True:
        current = set(scan_beatmaps())
        new_maps = current - known
        if new_maps:
            print(f"[osu!megamix] {len(new_maps)} new maps detected!")
        known = current
        yield list(current)
        time.sleep(interval)

def select_mode():
    print("Select gamemode (Enter for default: osu!megamix):")
    print("1. osu!megamix")
    print("2. osu!")
    print("3. osu!taiko")
    print("4. osu!catch")
    print("5. osu!mania")
    choice = input("Enter number: ").strip()
    return {
        "": "osu!megamix",
        "1": "osu!megamix",
        "2": "osu",
        "3": "taiko",
        "4": "catch",
        "5": "mania"
    }.get(choice, "osu!megamix")

# ---------------- Core Engine ----------------
def run_megamix(interval=5):
    mode = select_mode()
    print(f"[osu!megamix] Mode selected: {mode}")

    pool_gen = watch_beatmaps(interval=interval)
    try:
        for beatmaps in pool_gen:
            if not beatmaps:
                print("[osu!megamix] No maps found, waiting for additions...")
                continue

            if mode == "osu!megamix":
                random.shuffle(beatmaps)
                play_queue = beatmaps[:POOL_SIZE] if POOL_SIZE else beatmaps
            else:
                # For non-megamix modes, filter by extension or metadata (placeholder)
                play_queue = [bm for bm in beatmaps if bm.suffix == ".osu"]

            print(f"[osu!megamix] Current queue: {len(play_queue)} maps")
            for bm in play_queue:
                print(f"[osu!megamix] Next: {bm.name}")
            print("[osu!megamix] --- Refresh ---")
    except KeyboardInterrupt:
        print("[osu!megamix] Session interrupted!")
    finally:
        with open(PLAYER_HISTORY, "a") as f:
            f.write(f"{mode}\n")
        print("[osu!megamix] History updated!")
        backup_assets()

# ---------------- Entry ----------------
if __name__ == "__main__":
    print("[osu!megamix] Live MEGAMIX engine starting...")
    run_megamix()
