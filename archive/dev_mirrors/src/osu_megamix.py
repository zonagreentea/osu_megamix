CANON_PARSE_MS = None
CANON_GAMEINIT_MS = None
CANON_FIRSTTICK_MS = None

#!/usr/bin/env python3
# osu!megamix — no-deps Route A
# - Tkinter visuals (stdlib)
# - afplay audio (macOS builtin)
# - parses .osu hitcircles (Mode 0) from ./beatmaps
#
# Controls:
# - Hit: Left click OR Z / X / Space / Enter
# - Quit: Esc (or close window)

import os
import sys
import time
import glob
import subprocess
import tkinter as tk
from dataclasses import dataclass
from typing import List, Optional, Tuple
import atexit
import math

CANON_BOOT_T0 = time.perf_counter()

def audio_now_ms(audio):
    if audio is None:
        return int(time.perf_counter() * 1000)
    if hasattr(audio, 'now_ms'):
        return int(audio.now_ms())
    return int(time.perf_counter() * 1000)

AFPLAY_LATENCY_MS = 120  # lock once for macOS afplay

UNBALLED = ('--unballed' in sys.argv)
BUILD_NAME = "imagination* 1a visual"
class AudioPlayer:
    def __init__(self, path):
        self.path = path
        self.proc = None
        self.t0 = None

    def start(self):
        p = self.path
        if not p:
            return False
        p = os.path.abspath(str(p))
        if not os.path.exists(p):
            return False
        self.proc = subprocess.Popen(["/usr/bin/afplay", "-q", p])
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

# ----------------------------
# Timing model (approx osu!std)
# ----------------------------
def clamp(x, a, b):
    return a if x < a else b if x > b else x

def ar_to_preempt_ms(ar: float) -> int:
    # AR 0 => 1800ms, AR 5 => 1200ms, AR 10 => 450ms
    if ar < 5:
        return int(1800 - 120 * ar)
    return int(1200 - 150 * (ar - 5))

def od_to_windows_ms(od: float) -> Tuple[int, int, int]:
    w300 = int(80 - 6 * od)
    w100 = int(140 - 8 * od)
    w50  = int(200 - 10 * od)
    return max(10, w300), max(20, w100), max(30, w50)

# ----------------------------
# Beatmap parse
# ----------------------------
def read_lines(path: str) -> List[str]:
    with open(path, "r", errors="ignore") as f:
        return f.read().splitlines()

def parse_kv(lines: List[str], section: str) -> dict:
    out = {}
    in_sec = False
    tag = f"[{section}]"
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("//"):
            continue
        if s.startswith("[") and s.endswith("]"):
            in_sec = (s == tag)
            continue
        if in_sec and ":" in s:
            k, v = s.split(":", 1)
            out[k.strip()] = v.strip()
    return out

def find_section(lines: List[str], section: str) -> List[str]:
    out = []
    in_sec = False
    tag = f"[{section}]"
    for raw in lines:
        s = raw.strip()
        if s.startswith("[") and s.endswith("]"):
            in_sec = (s == tag)
            continue
        if in_sec and s and not s.startswith("//"):
            out.append(s)
    return out

@dataclass
class HitObject:
    x: int
    y: int
    t_ms: int
    typ: int

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
    circles: List[HitObject]

def list_osu_files(root="beatmaps") -> List[str]:
    return sorted(glob.glob(os.path.join(root, "**", "*.osu"), recursive=True))

def parse_osu(osu_path: str) -> Beatmap:
    lines = read_lines(osu_path)
    gen = parse_kv(lines, "General")
    meta = parse_kv(lines, "Metadata")
    diff = parse_kv(lines, "Difficulty")

    audio = gen.get("AudioFilename", "").strip()
    mode = int((gen.get("Mode", "0").strip() or "0"))

    title = meta.get("Title", os.path.basename(osu_path))
    artist = meta.get("Artist", "Unknown")
    version = meta.get("Version", "Unknown")

    od = float((diff.get("OverallDifficulty", "5").strip() or "5"))
    ar = float((diff.get("ApproachRate", str(od)).strip() or str(od)))

    objs = []
    for row in find_section(lines, "HitObjects"):
        parts = row.split(",")
        if len(parts) < 4:
            continue
        try:
            x = int(parts[0]); y = int(parts[1]); t = int(parts[2]); typ = int(parts[3])
        except Exception:
            continue
        objs.append(HitObject(x=x, y=y, t_ms=t, typ=typ))

    circles = [o for o in objs if (o.typ & 1) == 1]
    circles.sort(key=lambda o: o.t_ms)

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
        circles=circles,
    )

# ----------------------------
# Audio (macOS builtin)
# ----------------------------
class SimpleReplay:
    def __init__(self, path='last_replay.omxr'):
        self.path = path
        self.f = open(self.path, 'w', encoding='utf-8')
        self.f.write('OMXR1\n')
        self.last = None
    def write(self, sim_t, mask, x, y):
        cur = (sim_t, mask, x, y)
        if cur == self.last:
            return
        self.f.write(f"{sim_t},{mask},{x},{y}\n")
        self.last = cur
    def close(self):
        try:
            self.f.close()
        except Exception:
            pass

class Afplay:
    def __init__(self):
        self.proc = None
        self.path = None

    def play(self, path: str):
        """Start audio playback via macOS /usr/bin/afplay. Returns True if process stays alive."""
        import subprocess, time, os
        self.path = path
        if not path or not os.path.exists(path):
            print("[audio] missing path:", path)
            return False

        # stop previous if any
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
        except Exception:
            pass

        cmd = ["/usr/bin/afplay", path]
        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.05)
            alive = (self.proc.poll() is None)
            if not alive:
                print("[audio] afplay exited immediately:", cmd)
            return alive
        except Exception as e:
            print("[audio] afplay launch failed:", cmd, "ERR:", e)
            return False

    def start(self, path: str = None):
        """Compat alias for callers expecting .start()."""
        if path is None:
            path = getattr(self, "path", None)
        if not path:
            return False
        return self.play(path)
class Game:
    def run(self):
        # forced canonical loop
        try:
            ok = (self.audio.start() if (getattr(self, 'audio', None) and not UNBALLED) else False)
            print('[audio.start]', ok)
        except Exception as e:
            print('[audio.start] ERR', e)
        try:
            self.root.after(0, self.tick)
            print('[loop] after(0,tick) scheduled')
            self.root.mainloop()
        finally:
            try:
                if getattr(self, 'audio', None): self.audio.stop()
            except Exception:
                pass

    def __init__(self, bm: Beatmap):
        global CANON_GAMEINIT_MS
        if CANON_GAMEINIT_MS is None:
            CANON_GAMEINIT_MS = int((time.perf_counter() - CANON_BOOT_T0) * 1000)
        self.bm = bm
        self.sync_offset_ms = int(getattr(self.bm, 'audio_lead_in', 0) or 0) + AFPLAY_LATENCY_MS

        # Window
        self.W, self.H = 1024, 768
        self.root = tk.Tk()
        self.root.title(f"osu!megamix — {bm.artist} - {bm.title} [{bm.version}]")
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H, bg="black", highlightthickness=0)
        self.canvas.pack()

        # Uniform scale + centered letterbox
        self.scale = min(self.W / 512.0, self.H / 384.0)
        play_w = 512.0 * self.scale
        play_h = 384.0 * self.scale
        self.off_x = int((self.W - play_w) / 2.0)
        self.off_y = int((self.H - play_h) / 2.0)

        # Circle sizing scales with playfield
        self.base_r = max(18, int(42 * self.scale))
        self.approach_extra = max(40, int(90 * self.scale))

        # Timing
        self.preempt = ar_to_preempt_ms(self.bm.ar)
        self.w300, self.w100, self.w50 = od_to_windows_ms(self.bm.od)

        # State
        self.start_perf = time.perf_counter()
        self.idx = 0

        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.h300 = 0
        self.h100 = 0
        self.h50 = 0
        self.miss = 0

        self.last_hit_ms = -999999
        self.pending_hit = False

        # Audio
        self.audio = Afplay()
        self.replay = SimpleReplay('last_replay.omxr')
        self.mouse_x = 256
        self.mouse_y = 192
        self.mask = 0

        # Bind controls
        self.canvas.bind("<Button-1>", self.on_hit)
        self.root.bind("<KeyPress-z>", self.on_hit)
        self.root.bind('<Motion>', self.on_motion)
        self.root.bind("<KeyPress-x>", self.on_hit)
        self.root.bind("<KeyPress-space>", self.on_hit)
        self.root.bind("<KeyPress-Return>", self.on_hit)
        self.root.bind("<Escape>", self.on_quit)
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)

    def now_ms(self) -> int:
        return int((time.perf_counter() - self.start_perf) * 1000)

    def map_to_screen(self, x, y) -> Tuple[int, int]:
        return int(x * self.scale) + self.off_x, int(y * self.scale) + self.off_y

    def on_hit(self, _evt=None):
        self.pending_hit = True

    def on_quit(self, _evt=None):
        try:
            self.audio.stop()
        finally:
            self.root.destroy()

    def judge(self, dt: int) -> int:
        dt = abs(dt)
        if dt <= self.w300: return 300
        if dt <= self.w100: return 100
        if dt <= self.w50:  return 50
        return 0

    def tick(self):
        # canonical timebase (audio clock minus sync offset)
        t_ms = audio_now_ms(getattr(self, 'audio', None)) - getattr(self, 'sync_offset_ms', 0)
        # record replay (mask is whatever your key logic sets)
        try:
            self.replay.write(int(t_ms), int(getattr(self, 'mask', 0)), int(getattr(self,'mouse_x',0)), int(getattr(self,'mouse_y',0)))
        except Exception:
            pass
        # hardball: clamp time so a bad audio clock can't haywire the sim
        now_ms = int(time.perf_counter() * 1000)
        if not hasattr(self, '_hb_last_ms'):
            self._hb_last_ms = t_ms if t_ms is not None else now_ms
        if t_ms is None or t_ms <= 0:
            t_ms = now_ms - getattr(self, 'sync_offset_ms', 0)
        # clamp forward jumps to 100ms per tick
        if t_ms - self._hb_last_ms > 100:
            t_ms = self._hb_last_ms + 100
        self._hb_last_ms = t_ms
        global CANON_FIRSTTICK_MS
        if CANON_FIRSTTICK_MS is None:
            CANON_FIRSTTICK_MS = int((time.perf_counter() - CANON_BOOT_T0) * 1000)
        # Misses: advance when past w50
        while self.idx < len(self.bm.circles) and t_ms > self.bm.circles[self.idx].t_ms + self.w50:
            self.miss += 1
            self.combo = 0
            self.idx += 1

        # Visible list
        visible = []
        j = self.idx
        while j < len(self.bm.circles):
            o = self.bm.circles[j]
            if o.t_ms - t_ms > self.preempt:
                break
            if t_ms <= o.t_ms + self.w50:
                visible.append(o)
            j += 1

        # Handle hit
        if self.pending_hit and (t_ms - self.last_hit_ms) > 25:
            self.pending_hit = False
            self.last_hit_ms = t_ms

            if visible:
                cand = min(visible, key=lambda o: abs(t_ms - o.t_ms))
                result = self.judge(t_ms - cand.t_ms)
                if result:
                    if result == 300: self.h300 += 1
                    elif result == 100: self.h100 += 1
                    else: self.h50 += 1

                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    self.score += result + self.combo * 2

                    k = self.idx
                    while k < len(self.bm.circles) and self.bm.circles[k] is not cand:
                        k += 1
                    self.idx = min(len(self.bm.circles), k + 1)
                else:
                    self.combo = 0
            else:
                self.combo = 0

        # Draw
        self.canvas.delete("all")

# DRAW_SLIDER_1A
        # sliders (simple linear restore)
        for sl in getattr(self.bm, 'sliders', []):
            st = sl['t_ms']
            et = st + sl.get('duration_ms', 600)
            if t_ms < st - 1500 or t_ms > et + 1500:
                continue
            x0,y0, x1,y1 = sl['x'], sl['y'], sl['ex'], sl['ey']
            # draw path
            self.canvas.create_line(x0, y0, x1, y1, fill='#6aa6ff', width=3)
            # draw start/end nodes
            r = 12
            self.canvas.create_oval(x0-r, y0-r, x0+r, y0+r, outline='#6aa6ff', width=2)
            self.canvas.create_oval(x1-r, y1-r, x1+r, y1+r, outline='#6aa6ff', width=2)
        # (optional) draw playfield bounds so framing is obvious
        play_w = int(512 * self.scale)
        play_h = int(384 * self.scale)
        self.canvas.create_rectangle(self.off_x, self.off_y, self.off_x + play_w, self.off_y + play_h, outline="#222222")

        for o in visible:
            sx, sy = self.map_to_screen(o.x, o.y)
            frac = clamp((o.t_ms - t_ms) / max(1, self.preempt), 0.0, 1.0)

            base_r = self.base_r
            app_r = int(base_r + self.approach_extra * frac)

            self.canvas.create_oval(sx-app_r, sy-app_r, sx+app_r, sy+app_r, outline="#c8c8c8", width=2)
            self.canvas.create_oval(sx-base_r, sy-base_r, sx+base_r, sy+base_r, fill="white", outline="black", width=3)

        title = f"{self.bm.artist} - {self.bm.title} [{self.bm.version}]"
        hud1 = f"Score: {self.score}    Combo: {self.combo} (Max {self.max_combo})"
        hud2 = f"300:{self.h300}  100:{self.h100}  50:{self.h50}  Miss:{self.miss}    AR:{self.bm.ar:.1f} OD:{self.bm.od:.1f}"
        hud3 = "Hit: Click or Z/X/Space/Enter    Quit: Esc"
        hud3 += f" | {BUILD_NAME} | boot→parse:{CANON_PARSE_MS}ms init:{CANON_GAMEINIT_MS}ms first:{CANON_FIRSTTICK_MS}ms"

        self.canvas.create_text(12, 12, anchor="nw", fill="white", font=("Helvetica", 16, "bold"), text=title)
        self.canvas.create_text(12, 44, anchor="nw", fill="white", font=("Helvetica", 14), text=hud1)
        self.canvas.create_text(12, 70, anchor="nw", fill="#b4b4b4", font=("Helvetica", 12), text=hud2)
        self.canvas.create_text(12, self.H-18, anchor="sw", fill="#b4b4b4", font=("Helvetica", 12), text=hud3)

        if getattr(self.bm, 'circles', None):
            end_ms = self.bm.circles[-1].t_ms + 3000
            if self.idx >= len(self.bm.circles) and t_ms > end_ms:
                self.on_quit()
                return

        self.root.after(8, self.tick)

def pick_map(osu_files: List[str]) -> str:
    if not sys.stdin.isatty() or "--first" in sys.argv:
        return osu_files[0]
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
    argv = sys.argv[1:]
    if argv and argv[0].endswith(".osu") and os.path.exists(argv[0]):
        osu_path = argv[0]
    else:
        # Ensure beatmaps dir exists
        os.makedirs('beatmaps', exist_ok=True)
        osu_files = list_osu_files('beatmaps')
        if not osu_files:
            print('[osu!megamix] No .osu files found under ./beatmaps')
            print('[osu!megamix] Drop .osu files anywhere under ./beatmaps/** and run again.')
            print('[osu!megamix] Tip: extract .osk into ./beatmaps/<SetName>/ (for now)')
            return
        osu_path = pick_map(osu_files)

    bm = parse_osu(osu_path)
    global CANON_PARSE_MS
    CANON_PARSE_MS = int((time.perf_counter() - CANON_BOOT_T0) * 1000)
    print(f"[osu!megamix] Selected: {bm.artist} - {bm.title} [{bm.version}]")
    print(f"[osu!megamix] Audio: {bm.audio_path or '(missing)'}")
print(f"[osu!megamix] Audio exists: {bool(bm.audio_path and os.path.exists(bm.audio_path))}")
    Game(bm).run()

if __name__ == "__main__":
    main()
