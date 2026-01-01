#!/usr/bin/env python3
import re, time, pathlib

P = pathlib.Path("src/osu_megamix.py")

def backup(txt: str) -> pathlib.Path:
    b = P.with_suffix(f".py.bak_auto_{int(time.time())}")
    b.write_text(txt, encoding="utf-8")
    return b

def ensure_import(txt: str, mod: str) -> str:
    if re.search(rf'^\s*import\s+{re.escape(mod)}\b', txt, re.M):
        return txt
    m = re.search(r'^(?:(?:from|import)[^\n]*\n)+', txt, re.M)
    if m:
        return txt[:m.end()] + f"import {mod}\n" + txt[m.end():]
    return f"import {mod}\n" + txt

def move_boot_t0_below_imports(txt: str) -> str:
    # Remove all existing CANON_BOOT_T0 lines
    txt = re.sub(r'^\s*CANON_BOOT_T0\s*=.*\n', '', txt, flags=re.M)
    txt = ensure_import(txt, "time")
    m = re.search(r'^(?:(?:from|import)[^\n]*\n)+', txt, re.M)
    ins = m.end() if m else 0
    if "CANON_BOOT_T0" not in txt:
        txt = txt[:ins] + "\nCANON_BOOT_T0 = time.perf_counter()\n" + txt[ins:]
    return txt

def add_build_name(txt: str) -> str:
    label = 'imagination* 1a visual'
    if re.search(r'^\s*BUILD_NAME\s*=', txt, re.M):
        txt = re.sub(r'^\s*BUILD_NAME\s*=\s*["\'][^"\']*["\']\s*$',
                     f'BUILD_NAME = "{label}"', txt, flags=re.M)
        return txt
    m = re.search(r'^(?:(?:from|import)[^\n]*\n)+\n', txt, re.M)
    ins = m.end() if m else 0
    return txt[:ins] + f'BUILD_NAME = "{label}"\n\n' + txt[ins:]

def end_tail_fix(txt: str) -> str:
    # Replace last-circle+1200 with last-object+3000 (safe)
    pat = r'if\s+self\.idx\s*>=\s*len\(self\.bm\.circles\)\s*and\s*t_ms\s*>\s*self\.bm\.circles\[-1\]\.t_ms\s*\+\s*1200\s*:\s*\n\s*self\.on_quit\(\)\s*\n\s*return'
    rep = (
        "if getattr(self.bm, 'circles', None):\n"
        "            end_ms = self.bm.circles[-1].t_ms + 3000\n"
        "            if self.idx >= len(self.bm.circles) and t_ms > end_ms:\n"
        "                self.on_quit()\n"
        "                return"
    )
    return re.sub(pat, rep, txt)

def slider_restore(txt: str) -> str:
    """
    Minimal slider restoration:
    - parse HitObjects lines with type bit 2 (slider)
    - store as bm.sliders list of dicts {t_ms,x,y,ex,ey,duration_ms}
    - in tick(): treat slider start like a circle + draw path line + end marker
    This is intentionally simple + safe.
    """
    txt = ensure_import(txt, "math")

    # 1) ensure beatmap object has sliders container
    if "bm.sliders" not in txt:
        # best effort: after bm.circles = [] or similar initialization
        txt = re.sub(r'(bm\.circles\s*=\s*\[\]\s*\n)', r'\1    bm.sliders = []\n', txt, count=1)

    # 2) inject slider parse inside parse_osu HitObjects loop (best-effort)
    # Look for a place that appends circles; add slider handling nearby.
    if "SLIDER_RESTORE_1A" not in txt:
        marker = "# SLIDER_RESTORE_1A"
        # Common pattern: for ln in hitobjects: ... parts = ln.split(',')
        m = re.search(r'(for\s+.*in\s+hitobjects.*:\s*\n(?:[^\n]*\n){0,25}?\s*parts\s*=\s*.*split\(\s*[\'"]\,?[\'"]\s*\).*\n)', txt)
        if m:
            inject = (
                f"{marker}\n"
                "            # slider: type bit 2\n"
                "            try:\n"
                "                obj_type = int(parts[3])\n"
                "            except Exception:\n"
                "                obj_type = 0\n"
                "            if obj_type & 2:\n"
                "                # parts: x,y,time,type,hitSound,curve|...,slides,length,...\n"
                "                x = int(parts[0]); y = int(parts[1]); t = int(parts[2])\n"
                "                curve = parts[5] if len(parts) > 5 else ''\n"
                "                slides = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else 1\n"
                "                length = float(parts[7]) if len(parts) > 7 else 0.0\n"
                "                # linear fallback: use last control point if present\n"
                "                ex, ey = x, y\n"
                "                if '|' in curve:\n"
                "                    cps = curve.split('|')[1:]\n"
                "                    if cps:\n"
                "                        try:\n"
                "                            ex, ey = map(int, cps[-1].split(':'))\n"
                "                        except Exception:\n"
                "                            ex, ey = x, y\n"
                "                # duration fallback: length * slides (very rough) — better than missing sliders\n"
                "                duration_ms = int(max(300, (length * slides)))\n"
                "                bm.sliders.append({'t_ms': t, 'x': x, 'y': y, 'ex': ex, 'ey': ey, 'duration_ms': duration_ms})\n"
                "                continue\n"
            )
            txt = txt.replace(m.group(1), m.group(1) + inject, 1)

    # 3) draw sliders in tick(): find where circles are drawn, add slider draw before circles
    if "DRAW_SLIDER_1A" not in txt:
        marker = "# DRAW_SLIDER_1A"
        # Find a canvas delete call then draw calls; insert after delete to keep it visible
        m = re.search(r'(\s*self\.canvas\.delete\([^\n]*\)\s*\n)', txt)
        if m:
            inject = (
                f"{marker}\n"
                "        # sliders (simple linear restore)\n"
                "        for sl in getattr(self.bm, 'sliders', []):\n"
                "            st = sl['t_ms']\n"
                "            et = st + sl.get('duration_ms', 600)\n"
                "            if t_ms < st - 1500 or t_ms > et + 1500:\n"
                "                continue\n"
                "            x0,y0, x1,y1 = sl['x'], sl['y'], sl['ex'], sl['ey']\n"
                "            # draw path\n"
                "            self.canvas.create_line(x0, y0, x1, y1, fill='#6aa6ff', width=3)\n"
                "            # draw start/end nodes\n"
                "            r = 12\n"
                "            self.canvas.create_oval(x0-r, y0-r, x0+r, y0+r, outline='#6aa6ff', width=2)\n"
                "            self.canvas.create_oval(x1-r, y1-r, x1+r, y1+r, outline='#6aa6ff', width=2)\n"
            )
            txt = txt.replace(m.group(1), m.group(1) + inject, 1)

    return txt

def main():
    txt = P.read_text(encoding="utf-8")
    b = backup(txt)

    txt2 = txt
    txt2 = move_boot_t0_below_imports(txt2)
    txt2 = add_build_name(txt2)
    txt2 = end_tail_fix(txt2)
    txt2 = slider_restore(txt2)

    P.write_text(txt2, encoding="utf-8")
    changed = (txt != txt2)
    print("patched:", P)
    print("backup :", b)
    print("changed:", "yes" if changed else "no")

if __name__ == "__main__":
    main()
