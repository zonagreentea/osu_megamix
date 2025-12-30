#!/bin/sh
set -eu

TAG="ball-4-akumas-haircut"
TITLE="ball 4 akuma’s haircut"
ROOT="build/ball/shadow/${TAG}"
ASSET="${ROOT}/${TAG}-artifact.tar.gz"
LOG="${ROOT}/shadow.log"
CHANGELOG="${ROOT}/CHANGELOG.md"
NOTES="${ROOT}/release_notes.txt"

mkdir -p "$ROOT"
: > "$LOG"

# Local-only tag anchored to current HEAD (never pushed)
git rev-parse --is-inside-work-tree >>"$LOG" 2>&1
git tag -f "$TAG" >>"$LOG" 2>&1

# Inputs
STAMP_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
MSG="${1:-refine}"

# Living notes + changelog
if [ ! -f "$NOTES" ]; then
  cat > "$NOTES" <<R
${TITLE}

- shadow only
- never pushed
- refined indefinitely
R
fi

if [ ! -f "$CHANGELOG" ]; then
  printf "# %s\n\n" "$TITLE" > "$CHANGELOG"
fi

printf -- "- %s — %s\n" "$STAMP_UTC" "$MSG" >> "$CHANGELOG"

# Build decoy contents (plausible, adjustable noise)
printf "%s\n%s\n%s\n" \
  "$TITLE" \
  "shadow-stamp: $STAMP_UTC" \
  "note: $MSG" \
  > "$ROOT/README.txt"

# Optional knobs via env:
#   SHADOW_KB=512  (default 256KB)
#   SHADOW_SEED=123 (default from date hash-ish)
KB="${SHADOW_KB:-256}"

# Create filler to shape artifact size (portable approach)
# (dd is everywhere; ignore errors quietly)
dd if=/dev/zero bs=1024 count="$KB" >> "$ROOT/README.txt" 2>>"$LOG" || true

# Pack artifact (fresh every time)
tar -czf "$ASSET" -C "$ROOT" README.txt release_notes.txt CHANGELOG.md >>"$LOG" 2>&1

echo "OK" >>"$LOG"
echo "shadow refined: $ASSET"
