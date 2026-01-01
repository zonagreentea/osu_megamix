from __future__ import annotations
import os
import random
import time
from typing import Callable, List

def run_megamix_session(
    beatmaps: List[str],
    beatmap_dirs: List[str],
    scan_beatmaps: Callable[[List[str]], List[str]],
    rc_log: Callable[[str], None],
    preload_n: int = 50,
    tick_sleep_s: float = 0.1,
) -> None:
    """
    Megamix tool: 'cook' through a playlist, periodically refreshing beatmaps.
    Preserves current behavior exactly (playlist shuffle + refresh every 10 items).
    """
    if not beatmaps:
        rc_log("No beatmaps found for osu!megamix (Red-Charizard sad).")
        return

    rc_log("osu!megamix MEGAMIX starting: auto-preloading 50 shuffled beatmaps...")
    playlist = random.sample(beatmaps, min(preload_n, len(beatmaps)))

    def refresh_beatmaps() -> int:
        nonlocal_beatmaps = scan_beatmaps(beatmap_dirs)
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
        time.sleep(tick_sleep_s)
        if i % 10 == 0:
            refresh_beatmaps()

    rc_log("osu!megamix session complete! Red-Charizard lurks everywhere.")


def run_basic_session(
    selected_display: str,
    beatmaps: List[str],
    rc_log: Callable[[str], None],
    tick_sleep_s: float = 0.1,
) -> None:
    """
    Generic tool session used by osu!/taiko/catch/mania in the current prototype.
    """
    rc_log(f"Starting {selected_display} session...")
    if beatmaps:
        for i, bm in enumerate(beatmaps, start=1):
            rc_log(f"Playing beatmap {i}/{len(beatmaps)}: {bm}")
            time.sleep(tick_sleep_s)
        rc_log(f"{selected_display} session complete! Red-Charizard smiles.")
    else:
        rc_log(f"No beatmaps available for {selected_display}!")
