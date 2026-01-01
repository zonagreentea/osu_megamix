#!/usr/bin/env python3
# osu!megamix META MODE — stdlib only, cross-platform, gameplay-first.
import os, sys, time, glob

# ----------------------------
# Config (hardwire: no offset sliders)
# ----------------------------
W300, W100, W50 = 45, 90, 135
PREEMPT_MS = 900

def clamp(x,a,b): return a if x<a else b if x>b else x

def grade(err_ms):
    a = abs(int(err_ms))
    if a <= W300: return 300
    if a <= W100: return 100
    if a <= W50:  return 50
    return 0

# ----------------------------
# Beatmap: ultra-lite parser
# ----------------------------
class Obj:
    __slots__ = ("x","y","t")
    def __init__(self,x,y,t): self.x=x; self.y=y; self.t=t

class Beatmap:
    def __init__(self, osu_path):
        self.osu_path = osu_path
        self.audio_path = None
        self.objects = []
        self._parse()

    def _parse(self):
        base = os.path.dirname(self.osu_path)
        in_general = False
        in_hit = False
        with open(self.osu_path, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                line = raw.strip()
                if not line: 
                    continue
                if line.startswith("[") and line.endswith("]"):
                    in_general = (line == "[General]")
                    in_hit = (line == "[HitObjects]")
                    continue
                if in_general and line.startswith("AudioFilename:"):
                    af = line.split(":",1)[1].strip()
                    cand = os.path.join(base, af)
                    if os.path.exists(cand):
                        self.audio_path = cand
                if in_hit and "," in line:
                    parts = line.split(",")
                    if len(parts) >= 3:
                        try:
                            x = int(parts[0]); y = int(parts[1]); t = int(parts[2])
                            self.objects.append(Obj(x,y,t))
                        except:
                            pass
        self.objects.sort(key=lambda o:o.t)

def list_osu_files(root="beatmaps"):
    return sorted(glob.glob(os.path.join(root, "**", "*.osu"), recursive=True))

# ----------------------------
# Meta audio: NullAudio (no deps)
# ----------------------------
class NullAudio:
    def start(self, path=None): return False
    def stop(self): return None

# ----------------------------
# Renderer selection
# ----------------------------
def try_tk():
    try:
        import tkinter as tk
        return tk
    except Exception:
        return None

# ----------------------------
# Game core (deterministic sim clock)
# ----------------------------
class Game:
    def __init__(self, bm: Beatmap, use_ui=True):
        self.bm = bm
        self.audio = NullAudio()          # hardwire: no external audio
        self.use_ui = use_ui

        self.idx = 0
        self.combo = 0
        self.max_combo = 0
        self.score = 0
        self.h300 = self.h100 = self.h50 = self.miss = 0

        # input latch
        self.pending_hit = False
        self.last_hit_t = -10**9

        # canonical timebase
        self.t0 = time.perf_counter()
        self.map_zero_ms = 0  # map time 0 aligns to sim start (no offsets)

        # cursor (for future)
        self.cx = 256
        self.cy = 192

    def sim_ms(self):
        return int((time.perf_counter() - self.t0) * 1000)

    def map_ms(self):
        return self.sim_ms() - self.map_zero_ms

    def visible(self, t_ms):
        out=[]
        j=self.idx
        while j < len(self.bm.objects):
            o=self.bm.objects[j]
            if o.t - t_ms > PREEMPT_MS: break
            if t_ms <= o.t + W50: out.append(o)
            j += 1
        return out

    def apply_hit(self, t_ms, vis):
        if not vis:
            self.combo = 0
            return
        cand = min(vis, key=lambda o: abs(t_ms - o.t))
        err = t_ms - cand.t
        g = grade(err)
        if g:
            if g==300: self.h300 += 1
            elif g==100: self.h100 += 1
            else: self.h50 += 1
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.score += g + self.combo * 2
            # advance idx to after cand
            k=self.idx
            while k < len(self.bm.objects) and self.bm.objects[k] is not cand:
                k += 1
            self.idx = min(len(self.bm.objects), k+1)
        else:
            self.combo = 0

    def headless_loop(self):
        print("\nMETA MODE (headless): press ENTER to hit, Ctrl+C quits.\n")
        while self.idx < len(self.bm.objects):
            t_ms = self.map_ms()
            # misses
            while self.idx < len(self.bm.objects) and t_ms > self.bm.objects[self.idx].t + W50:
                self.miss += 1
                self.combo = 0
                self.idx += 1

            vis = self.visible(t_ms)
            try:
                input()  # ENTER = hit
            except KeyboardInterrupt:
                break
            t_ms = self.map_ms()
            self.apply_hit(t_ms, vis)
            print(f"t={t_ms:6d}  idx={self.idx:4d}  300={self.h300} 100={self.h100} 50={self.h50} miss={self.miss} combo={self.combo} score={self.score}")
        print("\nDONE",
              f"score={self.score}",
              f"max_combo={self.max_combo}",
              f"300={self.h300} 100={self.h100} 50={self.h50} miss={self.miss}")

    def tk_loop(self):
        tk = try_tk()
        if tk is None:
            print("[meta] tkinter not available -> headless mode")
            return self.headless_loop()

        root = tk.Tk()
        root.title("osu!megamix meta mode (stdlib-only)")
        W,H = 900,600
        canvas = tk.Canvas(root, width=W, height=H, bg="black", highlightthickness=0)
        canvas.pack()

        # map space 512x384 -> screen
        scale = min(W/512, H/384)
        offx = (W - 512*scale)/2
        offy = (H - 384*scale)/2

        def map_to_screen(x,y):
            return int(offx + x*scale), int(offy + y*scale)

        def on_space(_e=None):
            self.pending_hit = True

        def on_motion(e):
            self.cx, self.cy = int(e.x), int(e.y)

        root.bind("<space>", on_space)
        root.bind("<Button-1>", on_space)
        root.bind("<Motion>", on_motion)

        def tick():
            t_ms = self.map_ms()

            # misses
            while self.idx < len(self.bm.objects) and t_ms > self.bm.objects[self.idx].t + W50:
                self.miss += 1
                self.combo = 0
                self.idx += 1

            vis = self.visible(t_ms)

            # hit gating (simple debounce)
            if self.pending_hit and (t_ms - self.last_hit_t) > 25:
                self.pending_hit = False
                self.last_hit_t = t_ms
                self.apply_hit(t_ms, vis)

            # draw
            canvas.delete("all")

            # HUD
            canvas.create_text(12, 12, anchor="nw", fill="white",
                               text=f"t={t_ms}ms  score={self.score}  combo={self.combo}  miss={self.miss}  300/100/50={self.h300}/{self.h100}/{self.h50}")

            # objects
            for o in vis:
                sx,sy = map_to_screen(o.x,o.y)
                frac = clamp((o.t - t_ms) / max(1, PREEMPT_MS), 0.0, 1.0)
                base_r = int(36*scale)
                app_r = int((36 + 48*frac)*scale)
                canvas.create_oval(sx-app_r, sy-app_r, sx+app_r, sy+app_r, outline="#c8c8c8", width=2)
                canvas.create_oval(sx-base_r, sy-base_r, sx+base_r, sy+base_r, fill="white", outline="black", width=3)

            # end condition
            if self.idx >= len(self.bm.objects):
                canvas.create_text(W//2, H//2, fill="white", text="DONE", font=("Helvetica", 24))
                return

            root.after(8, tick)  # ~120Hz-ish
        tick()
        root.mainloop()

def main():
    os.makedirs("beatmaps", exist_ok=True)
    osu = list_osu_files("beatmaps")
    if not osu:
        print("[meta] No .osu found under ./beatmaps/**")
        print("[meta] Put .osk extracts into ./beatmaps/<SetName>/ and rerun.")
        return

    # pick first or user-provided index
    for i,p in enumerate(osu, start=1):
        print(f"{i:2d}. {p}")
    s = input("Pick number (default 1): ").strip()
    idx = int(s)-1 if (s.isdigit() and 1 <= int(s) <= len(osu)) else 0

    bm = Beatmap(osu[idx])
    print("[meta] Selected:", os.path.basename(bm.osu_path))
    if bm.audio_path:
        print("[meta] Audio present but disabled in no-deps build:", os.path.basename(bm.audio_path))
    else:
        print("[meta] No audio referenced or found (fine)")

    use_ui = ("--headless" not in sys.argv)
    Game(bm, use_ui=use_ui).tk_loop() if use_ui else Game(bm, use_ui=False).headless_loop()

if __name__ == "__main__":
    main()
