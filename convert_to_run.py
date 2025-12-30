#!/usr/bin/env python3
import sys, zipfile
from pathlib import Path

TICKRATE = 100

def header(cs=4.0, od=8.0, ar=9.0):
    return [
        "run osu.playcode:",
        f"  tickrate {TICKRATE}",
        "  mode megamix",
        f"  cs {cs}",
        f"  od {od}",
        f"  ar {ar}",
        "",
        "bind cursor from tablet abs",
        "bind cursor from mouse abs fallback",
        "bind cursor from mouse rel fallback",
        "bind cursor from keyboard axis fallback",
        "bind hit from any.button",
        "bind slow from key TAB toggle reset",
        ""
    ]

def parse_osu(text):
    cs, od, ar = 4.0, 8.0, 9.0
    objs = []
    sec = None
    oid = 1
    for line in text.splitlines():
        l = line.strip()
        if not l or l.startswith("//"):
            continue
        if l.startswith("[") and l.endswith("]"):
            sec = l[1:-1]
            continue
        if sec == "Difficulty" and ":" in l:
            k, v = l.split(":", 1)
            try:
                if k == "CircleSize": cs = float(v)
                elif k == "OverallDifficulty": od = float(v)
                elif k == "ApproachRate": ar = float(v)
            except:
                pass
        if sec == "HitObjects":
            p = l.split(",")
            if len(p) < 4:
                continue
            try:
                x, y, t, typ = int(p[0]), int(p[1]), int(p[2]), int(p[3])
            except:
                continue
            if typ & 1: kind = "circle"
            elif typ & 2: kind = "slider"
            elif typ & 8: kind = "spinner"
            else: kind = "unknown"
            objs.append((oid, kind, t, x, y, l))
            oid += 1
    return cs, od, ar, objs

def write_run(path, head, objs):
    with open(path, "w", encoding="utf-8") as f:
        for l in head:
            f.write(l + "\n")
        f.write("# objects\n")
        for oid, kind, t, x, y, raw in objs:
            if kind == "circle":
                f.write(f"object circle id {oid} at {t}ms pos ({x},{y})\n")
            else:
                raw = raw.replace("\"", "\\\"")
                f.write(f"object {kind} id {oid} at {t}ms pos ({x},{y}) raw \"{raw}\"\n")
        f.write("\nrule hitcircle:\n")
        f.write("  r = radius(cs)\n")
        f.write("  inside = segment_dist(cursor.prev, cursor.now, obj.pos) <= r\n")
        f.write("  timeok = abs(now - obj.time) <= window_for(od)\n")
        f.write("  hit when inside and timeok -> judge\n")
        f.write("\non reset: slow off; cursor.vel = (0,0); clear edges\n")

def convert_mix(p, outdir):
    text = None
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                if n.lower().endswith(".osu"):
                    text = z.read(n).decode("utf-8", "ignore")
                    break
    else:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except:
            pass
    if not text:
        write_run(outdir / (p.stem + ".run"), header(), [])
        return
    cs, od, ar, objs = parse_osu(text)
    write_run(outdir / (p.stem + ".run"), header(cs, od, ar), objs)

def convert_osk(p, outdir):
    out = outdir / (p.stem + "_skin.run")
    with open(out, "w", encoding="utf-8") as f:
        f.write("run osu.playcode:\n")
        f.write(f"  tickrate {TICKRATE}\n")
        f.write("  mode megamix\n\n")
        f.write(f"skin \"{p.stem}\":\n")
        if zipfile.is_zipfile(p):
            with zipfile.ZipFile(p) as z:
                for n in sorted(z.namelist()):
                    if not n.endswith("/"):
                        f.write(f"  file \"{n}\"\n")

def main():
    if len(sys.argv) != 3:
        print("usage: convert_to_run.py INDIR OUTDIR", file=sys.stderr)
        return 2
    indir = Path(sys.argv[1])
    outdir = Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    for p in indir.rglob("*"):
        if p.suffix.lower() == ".mix":
            convert_mix(p, outdir)
        elif p.suffix.lower() == ".osk":
            convert_osk(p, outdir)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
