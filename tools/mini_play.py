#!/usr/bin/env python3
import os, sys, time, glob, subprocess

W300, W100, W50 = 45, 90, 135

def grade(err):
    a = abs(int(err))
    if a <= W300: return 300
    if a <= W100: return 100
    if a <= W50:  return 50
    return 0

def list_osu():
    return sorted(glob.glob(os.path.join("beatmaps","**","*.osu"), recursive=True))

def find_audio(osu_path):
    # ultra-lite: parse AudioFilename from [General]
    audio = None
    in_general = False
    with open(osu_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line=line.strip()
            if line == "[General]": in_general = True; continue
            if line.startswith("[") and line.endswith("]") and line != "[General]": in_general = False
            if in_general and line.startswith("AudioFilename:"):
                audio = line.split(":",1)[1].strip()
                break
    if not audio: return None
    cand = os.path.join(os.path.dirname(osu_path), audio)
    return cand if os.path.exists(cand) else None

def load_hit_times(osu_path):
    times=[]
    in_hit=False
    with open(osu_path,"r",encoding="utf-8",errors="ignore") as f:
        for line in f:
            line=line.strip()
            if line == "[HitObjects]": in_hit=True; continue
            if in_hit and line and line[0] == "[": break
            if in_hit and line and "," in line:
                parts=line.split(",")
                if len(parts)>=3:
                    try: times.append(int(parts[2]))
                    except: pass
    times.sort()
    return times

def main():
    osu = list_osu()
    if not osu:
        print("No beatmaps found under ./beatmaps/**")
        return
    osu_path = osu[0]
    audio = find_audio(osu_path)
    times = load_hit_times(osu_path)
    print("MAP:", osu_path)
    print("AUDIO:", audio or "(missing)")
    if not times:
        print("No hitobjects found.")
        return

    t0 = time.perf_counter()
    proc = None
    if audio:
        ap = os.path.abspath(audio)
        proc = subprocess.Popen(["/usr/bin/afplay","-q", ap],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.perf_counter()

    i=0
    score=0
    combo=0
    print("\nPress ENTER to hit. Ctrl+C quits.\n")
    while i < len(times):
        now = int((time.perf_counter()-t0)*1000)
        # auto-miss
        if now > times[i] + W50:
            combo = 0
            i += 1
            continue

        s = input()  # enter = hit
        now = int((time.perf_counter()-t0)*1000)
        err = now - times[i]
        g = grade(err)
        if g:
            combo += 1
            score += g + combo*2
            print(f"{g:3d}  err={err:+4d}ms  combo={combo}  score={score}")
            i += 1
        else:
            combo = 0
            print(f"MISS err={err:+4d}ms")

    print("\nDONE score=",score,"combo_max not tracked")
    if proc:
        try: proc.terminate()
        except: pass

if __name__ == "__main__":
    main()
