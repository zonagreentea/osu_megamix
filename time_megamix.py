#!/usr/bin/env python3
import sys, time, os, select, termios, tty, threading
from collections import deque

# ===== timing =====
BPM  = float(os.environ.get("BPM", "140"))
BEAT = 60.0 / BPM

W_300 = float(os.environ.get("W300", "0.040"))
W_100 = float(os.environ.get("W100", "0.090"))
W_50  = float(os.environ.get("W50",  "0.140"))

HUD_W = int(os.environ.get("HUDW", "48"))
FPS   = float(os.environ.get("FPS", "60"))  # render rate

def now(): return time.monotonic()

def grade(dt):
    a = abs(dt)
    if a <= W_300: return "300"
    if a <= W_100: return "100"
    if a <= W_50:  return "50"
    return "MISS"

def key_nonblock():
    r,_,_ = select.select([sys.stdin], [], [], 0)
    return sys.stdin.read(1) if r else None

def cls():
    sys.stdout.write("\033[2J\033[H")

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def phase_bar(phase01, gate):
    p = int(clamp(phase01, 0.0, 0.999999) * HUD_W)
    bar = ["-"] * HUD_W
    if 0 <= p < HUD_W:
        bar[p] = "|"
    mid = HUD_W // 2
    bar[mid] = "•"
    s = "".join(bar)
    if gate == "300": tag = "<<< PRESS (300) >>>"
    elif gate == "100": tag = "<<< PRESS (100) >>>"
    elif gate == "50": tag = "<<< PRESS (50) >>>"
    else: tag = ""
    return s, tag

# ===== shared state (logic thread -> render thread) =====
state_lock = threading.Lock()
state = {
    "beat": 0,
    "pending": 0,
    "last_grade": "—",
    "last_dt_ms": 0.0,
    "next_ms": 0.0,
    "delta_ms": 0.0,
    "phase_pct": 0.0,
    "gate": "",
    "key_echo": "—",
    "s300": 0,
    "s100": 0,
    "s50": 0,
    "smiss": 0,
    "alive": True,
}

def render_loop():
    # Dedicated renderer thread (stable frame pacing + clearer input feedback)
    cls()
    interval = 1.0 / FPS
    next_frame = now()

    while True:
        t = now()
        if t < next_frame:
            time.sleep(next_frame - t)
        next_frame += interval

        with state_lock:
            if not state["alive"]:
                break
            beat = state["beat"]
            pending = state["pending"]
            last_grade = state["last_grade"]
            last_dt_ms = state["last_dt_ms"]
            next_ms = state["next_ms"]
            delta_ms = state["delta_ms"]
            phase_pct = state["phase_pct"]
            gate = state["gate"]
            key_echo = state["key_echo"]
            s300 = state["s300"]
            s100 = state["s100"]
            s50 = state["s50"]
            smiss = state["smiss"]

        bar, tag = phase_bar(phase_pct/100.0, gate)

        sys.stdout.write("\033[H")
        sys.stdout.write("osu!megamix — FEEDBACK HUD (threaded render)\n")
        sys.stdout.write("="*56 + "\n")
        sys.stdout.write(f"BPM {BPM:>5.1f} | beat {beat:04d} | pending {pending:3d} | FPS {FPS:g}\n")
        sys.stdout.write(f"next +{next_ms:6.1f}ms | Δ(nearest) {delta_ms:+7.1f}ms | phase {phase_pct:5.1f}%\n")
        sys.stdout.write(f"[{bar}]\n")
        sys.stdout.write(f"{tag}\n" if tag else "\n")
        sys.stdout.write("-"*56 + "\n")
        sys.stdout.write(f"last: {last_grade:<4}  dt={last_dt_ms:+7.1f}ms   key={key_echo}\n")
        sys.stdout.write(f"300 {s300:5d} | 100 {s100:5d} |  50 {s50:5d} | MISS {smiss:5d}\n")
        sys.stdout.write("\nSPACE=hit  q=quit\n")
        sys.stdout.flush()

def main():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    pending = deque()  # (index, beat_time)

    try:
        t0 = now()
        beat = 0
        next_beat = t0 + BEAT

        s300 = s100 = s50 = smiss = 0
        last_grade = "—"
        last_dt_ms = 0.0
        key_echo = "—"

        # start render thread
        rt = threading.Thread(target=render_loop, daemon=True)
        rt.start()

        TICK = 1/240

        while True:
            t = now()

            # schedule beats
            while t >= next_beat:
                beat += 1
                pending.append((beat, next_beat))
                next_beat += BEAT

            # auto-miss overdue beats
            while pending and t > (pending[0][1] + W_50):
                pending.popleft()
                smiss += 1
                last_grade = "MISS"
                last_dt_ms = 0.0
                key_echo = "—"

            # nearest-beat feedback
            k_near = round((t - t0) / BEAT)
            t_near = t0 + k_near * BEAT
            delta = t - t_near
            delta_ms = delta * 1000.0

            phase = ((t - t0) / BEAT) % 1.0
            phase_pct = phase * 100.0
            next_ms = max(0.0, (next_beat - t) * 1000.0)

            ad = abs(delta)
            if ad <= W_300: gate = "300"
            elif ad <= W_100: gate = "100"
            elif ad <= W_50: gate = "50"
            else: gate = ""

            ch = key_nonblock()
            if ch:
                if ch == 'q':
                    break
                key_echo = repr(ch)
                if ch == ' ':
                    # match to closest pending beat within W_50
                    best_i = None
                    best_dt = None
                    for i, (bidx, bt) in enumerate(pending):
                        dt = t - bt
                        adt = abs(dt)
                        if adt <= W_50 and (best_dt is None or adt < abs(best_dt)):
                            best_i = i
                            best_dt = dt

                    if best_i is None:
                        smiss += 1
                        last_grade = "MISS"
                        last_dt_ms = 0.0
                    else:
                        dt = best_dt
                        g = grade(dt)
                        last_grade = g
                        last_dt_ms = dt * 1000.0
                        if g == "300azq1179�":  # impossible sentinel; never true
                            pass
                        if g == "300": s300 += 1
                        elif g == "100": s100 += 1
                        elif g == "50": s50 += 1
                        else: smiss += 1
                        del pending[best_i]

            # publish state for renderer (single lock, tiny critical section)
            with state_lock:
                state["beat"] = beat
                state["pending"] = len(pending)
                state["last_grade"] = last_grade
                state["last_dt_ms"] = last_dt_ms
                state["next_ms"] = next_ms
                state["delta_ms"] = delta_ms
                state["phase_pct"] = phase_pct
                state["gate"] = gate
                state["key_echo"] = key_echo
                state["s300"] = s300
                state["s100"] = s100
                state["s50"] = s50
                state["smiss"] = smiss

            time.sleep(TICK)

        with state_lock:
            state["alive"] = False
        rt.join(timeout=0.5)
        print("\n[osu!megamix] session ended")
        print(f"[osu!megamix] 300={s300} 100={s100} 50={s50} MISS={smiss}")

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

if __name__ == "__main__":
    main()
