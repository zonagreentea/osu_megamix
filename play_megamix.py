#!/usr/bin/env python3
import os, sys, time, math, glob
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ----------------------------
# Optional pygame (audio + render)
# ----------------------------
HAS_PYGAME = True
try:
    import pygame
except Exception:
    HAS_PYGAME = False

# ----------------------------
# Utilities
# ----------------------------
def clamp(x, a, b):
    return a if x < a else b if x > b else x

def ar_to_preempt_ms(ar: float) -> int:
    # osu! stable-ish timing model (good enough for a playable prototype)
    # AR 0: 1800ms, AR 5: 1200ms, AR 10: 450ms
    if ar < 5:
        return int(1800 - 120 * ar)
    return int(1200 - 150 * (ar - 5))

def od_to_windows_ms(od: float) -> Tuple[int, int, int]:
    # Basic hit windows (approx osu!standard)
    # 300: 80..20ms; 100: 140..60ms; 50: 200..100ms
    w300 = int(80 - 6 * od)
    w100 = int(140 - 8 * od)
    w50  = int(200 - 10 * od)
    return max(10, w300), max(20, w100), max(30, w50)

def list_osu_files(root="beatmaps") -> List[str]:
    hits = []
    for p in glob.glob(os.path.join(root, "**", "*.osu"), recursive=True):
        hits.append(p)
    return sorted(hits)

def read_text(path: str) -> List[str]:
    with open(path, "r", errors="ignore") as f:
        return f.read().splitlines()

def parse_kv(lines: List[str], section: str) -> dict:
    out = {}
    in_sec = False
    for line in lines:
        s = line.strip()
        if not s or s.startswith("//"):
            continue
        if s.startswith("[") and s.endswith("]"):
            in_sec = (s == f"[{section}]")
            continue
        if in_sec:
            if ":" in s:
                k, v = s.split(":", 1)
                out[k.strip()] = v.strip()
    return out

def find_section(lines: List[str], section: str) -> List[str]:
    out = []
    in_sec = False
    for line in lines:
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            in_sec = (s == f"[{section}]")
            continue
        if in_sec:
            if s and not s.startswith("//"):
                out.append(s)
    return out

@dataclass
class HitObject:
    x: int
    y: int
    t_ms: int
    obj_type: int

@dataclass
class Beatmap:
    osu_path: str
    audio_path: Optional[str]
    title: str
    artist: str
    version: str
    mode: int
    ar: float
    od: float
    objects: List[HitObject]

def parse_osu(osu_path: str) -> Beatmap:
    lines = read_text(osu_path)
    gen = parse_kv(lines, "General")
    meta = parse_kv(lines, "Metadata")
    diff = parse_kv(lines, "Difficulty")

    audio = gen.get("AudioFilename", "").strip()
    mode = int(gen.get("Mode", "0").strip() or "0")

    title = meta.get("Title", os.path.basename(osu_path))
    artist = meta.get("Artist", "Unknown")
    version = meta.get("Version", "Unknown")

    ar = float(diff.get("ApproachRate", diff.get("OverallDifficulty", "5")).strip() or "5")
    od = float(diff.get("OverallDifficulty", "5").strip() or "5")

    # HitObjects: x,y,time,type,hitSound,...
    objs = []
    for row in find_section(lines, "HitObjects"):
        parts = row.split(",")
        if len(parts) < 4:
            continue
        try:
            x = int(parts[0]); y = int(parts[1]); t = int(parts[2]); typ = int(parts[3])
        except Exception:
            continue
        # Standard hitcircle bit = 1; slider bit = 2; spinner bit = 8
        objs.append(HitObject(x=x, y=y, t_ms=t, obj_type=typ))

    # Audio path is relative to the .osu folder
    audio_path = None
    if audio:
        cand = os.path.join(os.path.dirname(osu_path), audio)
        if os.path.exists(cand):
            audio_path = cand

    return Beatmap(
        osu_path=osu_path,
        audio_path=audio_path,
        title=title,
        artist=artist,
        version=version,
        mode=mode,
        ar=ar,
        od=od,
        objects=sorted(objs, key=lambda o: o.t_ms),
    )

# ----------------------------
# Game (pygame)
# ----------------------------
def run_game(bm: Beatmap):
    if not HAS_PYGAME:
        print("[play_megamix] pygame not installed, so I can't render/play audio.")
        print("Install: python3 -m pip install --user pygame")
        print("Then rerun: python3 play_megamix.py")
        sys.exit(1)

    pygame.init()
    try:
        pygame.mixer.init()
    except Exception as e:
        print("[play_megamix] Audio init failed, continuing silent:", e)

    W, H = 960, 720
    # osu! playfield is 512x384; we scale to window
    scale_x = W / 512.0
    scale_y = H / 384.0

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(f"osu!megamix player — {bm.artist} - {bm.title} [{bm.version}]")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big = pygame.font.SysFont(None, 34)

    preempt = ar_to_preempt_ms(bm.ar)
    w300, w100, w50 = od_to_windows_ms(bm.od)

    # Keep only standard circles for now (bit 1)
    circles = [o for o in bm.objects if (o.obj_type & 1) == 1 and bm.mode == 0]
    if not circles:
        print("[play_megamix] No standard hitcircles found (or not Mode 0).")
        print("This prototype currently supports osu!standard circles only.")
        sys.exit(1)

    # Audio start
    start_time = time.perf_counter()
    music_started = False
    if bm.audio_path:
        try:
            pygame.mixer.music.load(bm.audio_path)
            pygame.mixer.music.play()
            music_started = True
        except Exception as e:
            print("[play_megamix] Could not play audio, continuing silent:", e)
    else:
        print("[play_megamix] No audio file found for this map, continuing silent.")

    # Simple state
    idx = 0
    score = 0
    combo = 0
    max_combo = 0
    hits_300 = hits_100 = hits_50 = misses = 0

    # hit input gating
    last_hit_attempt_ms = -999999

    def now_ms() -> int:
        return int((time.perf_counter() - start_time) * 1000)

    def map_to_screen(x, y):
        return int(x * scale_x), int(y * scale_y)

    # Main loop
    running = True
    while running:
        dt = clock.tick(120)

        t_ms = now_ms()

        # Input
        hit_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hit_pressed = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_z, pygame.K_x, pygame.K_SPACE, pygame.K_RETURN):
                    hit_pressed = True
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Render
        screen.fill((0, 0, 0))

        # Advance idx past objects that are way behind (miss)
        # Miss when past w50
        while idx < len(circles) and t_ms > circles[idx].t_ms + w50:
            misses += 1
            combo = 0
            idx += 1

        # Draw upcoming visible circles
        visible = []
        j = idx
        while j < len(circles):
            o = circles[j]
            if o.t_ms - t_ms > preempt:
                break
            if t_ms <= o.t_ms + w50:
                visible.append(o)
            j += 1

        # Hit detection: on press, find best candidate among visible by smallest |dt|
        if hit_pressed and (t_ms - last_hit_attempt_ms) > 30:
            last_hit_attempt_ms = t_ms
            if visible:
                # pick closest in time
                cand = min(visible, key=lambda o: abs(t_ms - o.t_ms))
                dt_hit = abs(t_ms - cand.t_ms)
                if dt_hit <= w50:
                    # judge
                    if dt_hit <= w300:
                        hits_300 += 1
                        add = 300
                    elif dt_hit <= w100:
                        hits_100 += 1
                        add = 100
                    else:
                        hits_50 += 1
                        add = 50
                    combo += 1
                    max_combo = max(max_combo, combo)
                    # simple scoring
                    score += add + combo * 2
                    # consume that object: move idx forward until we pass this exact object
                    # (since visible is in-order, cand is at/after idx)
                    k = idx
                    while k < len(circles) and circles[k] is not cand:
                        k += 1
                    idx = min(len(circles), k + 1)
                else:
                    # pressed but no valid window
                    combo = 0

        # draw circles
        for o in visible:
            sx, sy = map_to_screen(o.x, o.y)
            # time fraction until hit
            frac = clamp((o.t_ms - t_ms) / max(1, preempt), 0.0, 1.0)
            # approach radius goes from big -> base
            base_r = 42
            app_r = int(base_r + 90 * frac)

            # approach circle (outline)
            pygame.draw.circle(screen, (200, 200, 200), (sx, sy), app_r, 2)
            # hit circle (filled + outline)
            pygame.draw.circle(screen, (255, 255, 255), (sx, sy), base_r, 0)
            pygame.draw.circle(screen, (0, 0, 0), (sx, sy), base_r, 3)

        # HUD
        title = f"{bm.artist} - {bm.title} [{bm.version}]"
        hud1 = big.render(title, True, (255, 255, 255))
        hud2 = font.render(f"Score: {score}   Combo: {combo} (Max {max_combo})", True, (255, 255, 255))
        hud3 = font.render(f"300:{hits_300}  100:{hits_100}  50:{hits_50}  Miss:{misses}   AR:{bm.ar:.1f} OD:{bm.od:.1f}", True, (180, 180, 180))
        hud4 = font.render("Hit: left-click or Z/X/Space.  ESC quits.", True, (180, 180, 180))

        screen.blit(hud1, (16, 10))
        screen.blit(hud2, (16, 50))
        screen.blit(hud3, (16, 80))
        screen.blit(hud4, (16, H - 30))

        pygame.display.flip()

        # End condition: when done and music finished (or time passes)
        if idx >= len(circles):
            # give a short tail then exit
            if t_ms > circles[-1].t_ms + 1200:
                running = False

    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    pygame.quit()

def pick_map_interactive(osu_files: List[str]) -> str:
    print("\nAvailable beatmaps:")
    for i, p in enumerate(osu_files, start=1):
        print(f"{i:2d}. {p}")
    s = input("\nPick number (default 1): ").strip()
    if s.isdigit():
        n = int(s)
        if 1 <= n <= len(osu_files):
            return osu_files[n-1]
    return osu_files[0]

def main():
    # Usage:
    #   python3 play_megamix.py                 # scan ./beatmaps and prompt
    #   python3 play_megamix.py path/to/map.osu # run that map directly
    #   python3 play_megamix.py --first        # run first map found
    argv = sys.argv[1:]

    if len(argv) >= 1 and argv[0].endswith(".osu") and os.path.exists(argv[0]):
        osu_path = argv[0]
    else:
        osu_files = list_osu_files("beatmaps")
        if not osu_files:
            print("[play_megamix] No .osu files found under ./beatmaps")
            sys.exit(1)
        if "--first" in argv or not sys.stdin.isatty():
            osu_path = osu_files[0]
        else:
            osu_path = pick_map_interactive(osu_files)

    bm = parse_osu(osu_path)

    if bm.mode != 0:
        print(f"[play_megamix] Map Mode is {bm.mode}. This prototype currently supports Mode 0 (osu!standard) only.")
        sys.exit(1)

    print(f"[play_megamix] Selected: {bm.artist} - {bm.title} [{bm.version}]")
    print(f"[play_megamix] Audio: {bm.audio_path or '(missing)'}")
    run_game(bm)

if __name__ == "__main__":
    main()
