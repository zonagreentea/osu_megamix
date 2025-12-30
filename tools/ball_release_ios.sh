#!/bin/sh
set -eu

NUM=1
PLAT=ios
TAG="ball-${NUM}-${PLAT}"
TITLE="ball ${NUM} iOS"

OUT=build/ball
LOG="$OUT/release.log"
mkdir -p "$OUT"
: > "$LOG"

# Ensure we're in a git repo
git rev-parse --is-inside-work-tree >>"$LOG" 2>&1

# Build lib if missing
if [ ! -f "$OUT/libball.a" ]; then
  SDK_IOS="$(/usr/bin/xcrun --sdk iphoneos --show-sdk-path 2>>"$LOG" || true)"
  [ -n "$SDK_IOS" ] || { echo "no iphoneos sdk" >>"$LOG"; exit 1; }

  /usr/bin/xcrun clang -isysroot "$SDK_IOS" -arch arm64 -std=c17 -O2 \
    -c ball/ball.c -o "$OUT/ball.o" >>"$LOG" 2>&1

  /usr/bin/libtool -static -o "$OUT/libball.a" "$OUT/ball.o" >>"$LOG" 2>&1
fi

# Commit sources (not binary)
git add ball/ball.c ball/ball.h >>"$LOG" 2>&1 || true
git commit -m "$TITLE" >>"$LOG" 2>&1 || true

# Push branch + tag
git push -u origin HEAD >>"$LOG" 2>&1
git tag -f "$TAG" >>"$LOG" 2>&1
git push -f origin "$TAG" >>"$LOG" 2>&1

# Auth check (non-interactive)
gh auth status >>"$LOG" 2>&1 || { echo "gh not authed: run 'gh auth login' in a real terminal" >>"$LOG"; exit 2; }

# Create release targeting current commit; upload asset
SHA="$(git rev-parse HEAD)"
gh release create "$TAG" "$OUT/libball.a" \
  --title "$TITLE" \
  --notes "$TITLE" \
  --target "$SHA" \
  --latest >>"$LOG" 2>&1

echo "OK" >>"$LOG"
