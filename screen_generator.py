#!/usr/bin/env python3
"""Generate a standalone leaderboard screen from an HTML seed."""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def generate(seed_path):
    seed_path = Path(seed_path)
    if not seed_path.is_absolute():
        seed_path = ROOT / seed_path

    if not seed_path.is_file():
        raise SystemExit(f"screen generator: seed not found: {seed_path}")

    source = seed_path.read_text(encoding="utf-8")

    title_match = re.search(r"<title[^>]*>(.*?)</title>", source, re.I | re.S)
    title = html.escape(title_match.group(1).strip() if title_match else "osu!megamix")

    colors = re.findall(r"#[0-9a-fA-F]{6}\b", source)
    accent = colors[0] if colors else "#ff66aa"

    output = ROOT / "build" / "leaderboard.html"
    output.parent.mkdir(parents=True, exist_ok=True)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ranking · {title}</title>
<style>
:root {{ color-scheme: dark; --accent: {accent}; }}
* {{ box-sizing: border-box; }}
body {{
    margin: 0; min-height: 100vh; padding: 32px 18px;
    background: #101014; color: #f7f7fb;
    font: 16px/1.5 -apple-system, BlinkMacSystemFont, sans-serif;
}}
main {{ width: min(780px, 100%); margin: 0 auto; }}
header {{ border-bottom: 2px solid var(--accent); padding-bottom: 18px; }}
.eyebrow {{ color: var(--accent); font-size: 12px; font-weight: 800; letter-spacing: .16em; }}
h1 {{ margin: 8px 0 0; font-size: clamp(30px, 7vw, 48px); }}
.panel {{
    margin-top: 22px; padding: 22px;
    background: #1a1a22; border: 1px solid #34343f; border-radius: 12px;
}}
.label {{ color: #aaaab8; font-size: 12px; font-weight: 800; letter-spacing: .12em; }}
.score {{ margin-top: 6px; color: var(--accent); font-size: clamp(34px, 8vw, 54px); font-weight: 900; }}
table {{ width: 100%; margin-top: 22px; border-collapse: collapse; text-align: left; }}
th {{ color: #aaaab8; font-size: 12px; text-transform: uppercase; }}
th, td {{ padding: 14px 10px; border-bottom: 1px solid #34343f; }}
td:last-child, th:last-child {{ text-align: right; font-variant-numeric: tabular-nums; }}
.empty {{ padding: 26px 10px; color: #b9b9c7; text-align: center; }}
footer {{ margin-top: 22px; color: #888895; font-size: 13px; }}
</style>
</head>
<body>
<main>
<header>
    <div class="eyebrow">OSU!MEGAMIX · RANKING</div>
    <h1>Leaderboard</h1>
    <div>Seed: {title}</div>
</header>
<section class="panel" aria-label="Your score">
    <div class="label">YOUR SCORE</div>
    <div class="score" id="yourScore">—</div>
    <div id="scoreNote">Waiting for a score from the game.</div>
</section>
<section class="panel" aria-label="Player rankings">
    <div class="label">PLAYER RANKINGS</div>
    <table>
        <thead><tr><th>Rank</th><th>Player</th><th>Score</th></tr></thead>
        <tbody id="rankings">
            <tr><td colspan="3" class="empty">No shared scores available yet.</td></tr>
        </tbody>
    </table>
</section>
<footer>Generated from the game seed. Online rankings require a shared score source.</footer>
</main>
<script>
/* Real scores will be supplied by the game's score source.
   This screen deliberately does not invent player records. */
</script>
</body>
</html>
"""
    output.write_text(page, encoding="utf-8")
    print(f"Generated: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: run screen_generator.py osu_megamix.html")
    generate(sys.argv[1])
