from datetime import date, datetime
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
DAY = date(2026, 11, 11)

def is_remembrance_day(now=None):
    return (now or datetime.now()).date() == DAY

def launch():
    page = ROOT / "index.html"
    if not page.is_file():
        print("Remembrance: index.html is missing")
        return 1
    return subprocess.call(["open", str(page)])

if __name__ == "__main__":
    import sys
    if is_remembrance_day() or "--preview" in sys.argv:
        raise SystemExit(launch())
    print("Remembrance module inactive")
