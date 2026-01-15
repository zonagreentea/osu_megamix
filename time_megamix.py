#!/usr/bin/env python3
import sys, time, os, select, termios, tty
from collections import deque
from math import floor

BPM = float(os.environ.get("BPM", "140"))
BEAT = 60.0 / BPM

# judgement windows (seconds)
W_300 = float(os.environ.get("W300", "0.040"))
W_100 = float(os.environ.get("W100", "0.090"))
W_50  = float(os.environ.get("W50",  "0.140"))

HUD_W = int(os.environ.get("HUDW", "48"))  # width of phase bar

def now():
    return time.monotonic()

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

def phase_bar(phase, gate):
    # phase: 0..1
    # gate: "", "50", "100", "300"
    p = int(clamp(phase, 0.0, 0.999999) * HUD_W)
    bar = ["-"] * HUD_W
    if 0 <= p < HUD_W:
        bar[p] = "|"
    # mark perfect center with a dot (visual anchor)
    mid = HUD_W // 2
    bar[mid] = "•"
    s = "".join(bar)
    if gate == "300":
        tag = "<<< PRESS (300) >>>"
    elif gate == "100":
        tag = "<<< PRESS (100) >>>"
    elif gate == "50":
        tag = "<<< PRESS (50) >>>"
    else:
        tag = ""
    return s, tag

def hud(beat, pending, last_grade, last_dt_ms, next_ms, delta_ms, phase, gate, key_echo,
        s300, s100, s50, smiss):
    sys.stdout.write("\033[H")
    sys.stdout.write("osu!megamix — FEEDBACK HUD (terminal)\n")
    sys.stdout.write("="*56 + "\n")
    sys.stdout.write(f"BPM {BPM:>5.1f} | beat {beat:04d} | pending {pending:3d}\n")
    sys.stdout.write(f"next +{next_ms:6.1f}ms | Δ(nearest) {delta_ms:+7.1f}ms | phase {phase:5.1f}%\n")

    bar, tag = phase_bar(phase/100.0, gate)
    sys.stdout.write(f"[{bar}]\n")
    if tag:
        sys.stdout.write(f"{tag}\n")
    else:
        sys.stdout.write("\n")

    sys.stdout.write("-"*56 + "\n")
    sys.stdout.write(f"last: {last_grade:<4}  dt={last_dt_ms:+7.1f}ms   key={key_echo}\n")
    sys.stdout.write(f"300 {s300:5d} | 100 {s100:5d} |  50 {s50:5d} | MISS {smiss:5d}\n")
    sys.stdout.write("\nSPACE=hit  q=quit\n")
    sys.stdout.flush()

def main():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    try:
        cls()
        t0 = now()

        beat = 0
        next_beat = t0 + BEAT

        # pending beats: deque of (index, beat_time)
        pending = deque()

        s300 = s100 = s50 = smiss = 0
        last_grade = "—"
        last_dt_ms = 0.0
        key_echo = "—"

        TICK = 1/240

        # render once
        hud(beat, len(pending), last_grade, last_dt_ms, 0.0, 0.0, 0.0, "", key_echo,
            s300, s100, s50, smiss)

        while True:
            t = now()

            # schedule beats without drift
            while t >= next_beat:
                beat += 1
                pending.append((beat, next_beat))
                next_beat += BEAT

            # auto-miss anything older than W_50 past its beat time
            while pending and t > (pending[0][1] + W_50):
                pending.popleft()
                smiss += 1
                last_grade = "MISS"
                last_dt_ms = 0.0
                key_echo = "—"

            # nearest-beat delta live (for feedback)
            # nearest beat index around current time
            k_near = round((t - t0) / BEAT)
            t_near = t0 + k_near * BEAT
            delta = t - t_near  # seconds
            delta_ms = delta * 1000.0

            # phase in beat [0..1)
            phase = ((t - t0) / BEAT) % 1.0
            phase_pct = phase * 100.0

            # countdown to next scheduled beat
            next_ms = max(0.0, (next_beat - t) * 1000.0)

            # gate: which window are we currently inside (for "PRESS NOW")
            ad = abs(delta)
            if ad <= W_300:
                gate = "300"
            elif ad <= W_100:
                gate = "100"
            elif ad <= W_50:
                gate = "50"
            else:
                gate = ""

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
                        if g == "300": s300 += 1
                        elif g == "100": s100 += 1
                        elif g == "50": s50 += 1
                        else: smiss += 1
                        del pending[best_i]

            # render every frame (feedback engine)
            hud(beat, len(pending), last_grade, last_dt_ms, next_ms, delta_ms, phase_pct, gate, key_echo,
                s300, s100, s50, smiss)

            time.sleep(TICK)

        print("\n[osu!megamix] session ended")
        print(f"[osu!megamix] 300={s300} 100={s100} 50={s50} MISS={smiss}")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

if __name__ == "__main__":
    main()
