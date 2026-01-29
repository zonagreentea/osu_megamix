#!/usr/bin/env bash
set -euo pipefail

NAME="osu!megamix FFFFFF final"
SLUG="osu_megamix_FFFFFF_final"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1" >&2; exit 1; }; }
need python3
need tar
need zip

rm -rf "$DIST/tmp"
mkdir -p "$DIST/tmp"

# Files to ship (keep it minimal but functional)
copy_core() {
  local out="$1"
  mkdir -p "$out"
  cp -f "$ROOT/index.html" "$out/"
  mkdir -p "$out/src" "$out/tools" "$out/docs"
  [ -d "$ROOT/src" ] && cp -R "$ROOT/src/"* "$out/src/" 2>/dev/null || true
  [ -d "$ROOT/tools" ] && cp -R "$ROOT/tools/"* "$out/tools/" 2>/dev/null || true
  [ -d "$ROOT/docs" ] && cp -R "$ROOT/docs/"* "$out/docs/" 2>/dev/null || true
  # include mix file if it exists in repo root
  [ -f "$ROOT/osu!megamix.mix" ] && cp -f "$ROOT/osu!megamix.mix" "$out/" || true
  # sanity: gateway server must exist for absolute-mix canonical mode
  if [ ! -f "$out/tools/mix_server.py" ]; then
    echo "ERROR: tools/mix_server.py missing. (absolute mix mode needs gateway)" >&2
    exit 1
  fi
}

# Helper to create a URL at runtime (ABS path stays ABS, encoded)
# We rely on /__file gateway in mix_server + API resolver
make_url_py='import os,urllib.parse,sys
root=sys.argv[1]; mix=sys.argv[2]
print("http://127.0.0.1:8000/index.html?mix="+urllib.parse.quote(mix, safe="/:"))'

# ---------------- Windows ----------------
WIN="$DIST/tmp/windows"
copy_core "$WIN/app"

cat > "$WIN/START.bat" <<'BAT'
@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0app"

REM Find python
where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py -3
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set PY=python
  ) else (
    echo Python not found. Install Python 3, then re-run.
    pause
    exit /b 1
  )
)

REM Compute absolute mix path
set MIX=%cd%\osu!megamix.mix

REM Start server
start "" /B %PY% tools\mix_server.py 8000 127.0.0.1

REM Open browser to absolute mix
%PY% -c "import urllib.parse,os; mix=os.path.abspath(r'%MIX%'); print('http://127.0.0.1:8000/index.html?mix='+urllib.parse.quote(mix, safe='/:'))" > "%temp%\megamix_url.txt"
for /f "usebackq delims=" %%U in ("%temp%\megamix_url.txt") do set URL=%%U
start "" "!URL!"

echo osu!megamix running at:
echo !URL!
echo Close this window to stop (or use Task Manager to end python).
pause
BAT

mkdir -p "$DIST/windows"
( cd "$DIST/tmp/windows" && zip -qr "$DIST/windows/${SLUG}_windows.zip" . )

# ---------------- macOS ----------------
MAC="$DIST/tmp/macos"
copy_core "$MAC/app"

cat > "$MAC/START.command" <<'CMD'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/app"

PY=python3
command -v python3 >/dev/null 2>&1 || { echo "python3 missing"; exit 1; }

MIX="$(pwd)/osu!megamix.mix"

$PY tools/mix_server.py 8000 127.0.0.1 >/tmp/megamix_server.log 2>&1 &
PID=$!

URL="$($PY -c "import urllib.parse,os; mix=os.path.abspath('$MIX'); print('http://127.0.0.1:8000/index.html?mix='+urllib.parse.quote(mix, safe='/:'))")"

# open default browser
open "$URL" || true

echo "osu!megamix running at:"
echo "$URL"
echo "server pid=$PID"
echo "stop: kill $PID"
wait $PID
CMD
chmod +x "$MAC/START.command"

mkdir -p "$DIST/macos"
( cd "$DIST/tmp/macos" && tar -czf "$DIST/macos/${SLUG}_macos.tar.gz" . )

# ---------------- Linux ----------------
LIN="$DIST/tmp/linux"
copy_core "$LIN/app"

cat > "$LIN/start.sh" <<'CMD'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/app"

PY=python3
command -v python3 >/dev/null 2>&1 || { echo "python3 missing"; exit 1; }

MIX="$(pwd)/osu!megamix.mix"

$PY tools/mix_server.py 8000 127.0.0.1 >/tmp/megamix_server.log 2>&1 &
PID=$!

URL="$($PY -c "import urllib.parse,os; mix=os.path.abspath('$MIX'); print('http://127.0.0.1:8000/index.html?mix='+urllib.parse.quote(mix, safe='/:'))")"

# try common openers
( command -v xdg-open >/dev/null 2>&1 && xdg-open "$URL" ) || \
( command -v gio >/dev/null 2>&1 && gio open "$URL" ) || true

echo "osu!megamix running at:"
echo "$URL"
echo "server pid=$PID"
echo "stop: kill $PID"
wait $PID
CMD
chmod +x "$LIN/start.sh"

mkdir -p "$DIST/linux"
( cd "$DIST/tmp/linux" && tar -czf "$DIST/linux/${SLUG}_linux.tar.gz" . )

# ---------------- iOS (PWA / local host instructions) ----------------
IOS="$DIST/tmp/ios"
copy_core "$IOS/app"

cat > "$IOS/README_iOS.txt" <<'TXT'
osu!megamix iOS package (PWA-style)

This is not an App Store build. iOS browsers cannot run a background Python server.

Run options:
1) Host from your Mac/PC:
   - On Mac/Linux: run app/tools/mix_server.py
   - Then open on iPhone (same Wi-Fi) using your computer's LAN IP:
     http://<LAN-IP>:8000/index.html?mix=/Users/.../osu!megamix.mix

2) Use iSH (Alpine Linux on iOS) or similar to run python3 locally (advanced).
3) Add to Home Screen (PWA):
   - Open the URL in Safari
   - Share -> Add to Home Screen

Absolute mix stays absolute by design. The gateway server makes the file readable to the browser.
TXT

mkdir -p "$DIST/ios"
( cd "$DIST/tmp/ios" && zip -qr "$DIST/ios/${SLUG}_ios.zip" . )

# ---------------- Android (Termux instructions) ----------------
AND="$DIST/tmp/android"
copy_core "$AND/app"

cat > "$AND/README_Android.txt" <<'TXT'
osu!megamix Android package (Termux-friendly)

This is not a Play Store APK build.

Fast path:
1) Install Termux
2) In Termux:
   pkg update
   pkg install python
3) Copy this folder to your phone (e.g., Downloads/osu_megamix)
4) In Termux:
   cd ~/storage/downloads/osu_megamix/app
   python3 tools/mix_server.py 8000 127.0.0.1
5) Open in Chrome:
   http://127.0.0.1:8000/index.html?mix=/data/data/com.termux/files/home/storage/downloads/osu_megamix/app/osu!megamix.mix

Absolute mix stays absolute. The gateway endpoint serves it.
TXT

mkdir -p "$DIST/android"
( cd "$DIST/tmp/android" && zip -qr "$DIST/android/${SLUG}_android.zip" . )

# ---------------- Nintendo DS (homebrew placeholder) ----------------
NDS="$DIST/tmp/nds"
copy_core "$NDS/app"

cat > "$NDS/README_NDS.txt" <<'TXT'
osu!megamix Nintendo DS package (placeholder)

A real .nds build requires a dedicated homebrew toolchain (devkitPro) and a DS runtime.
This bundle ships the mix hub + assets as the canonical source.

Recommended: run osu!megamix on PC and treat DS as a controller/companion.
If you want a real DS port, we can:
- define an ultra-minimal DS front-end
- stream inputs / timeline from a host
- or build a dedicated DS renderer (big project)

Absolute mix is canon; DS would need its own storage mapping layer.
TXT

mkdir -p "$DIST/nds"
( cd "$DIST/tmp/nds" && zip -qr "$DIST/nds/${SLUG}_nds.zip" . )

echo "DONE. Packages:"
ls -la "$DIST/windows" "$DIST/macos" "$DIST/linux" "$DIST/ios" "$DIST/android" "$DIST/nds"
