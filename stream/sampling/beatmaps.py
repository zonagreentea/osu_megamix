from __future__ import annotations
import os
from typing import List

DEFAULT_BEATMAP_DIRS = ["osu_beatmaps", "osu_mix_beatmaps", "beatmaps"]

def scan_beatmaps(dirs: List[str]) -> List[str]:
    out: List[str] = []
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
