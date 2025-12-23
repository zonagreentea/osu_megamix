#!/usr/bin/env zsh
set -euo pipefail

REPO="${REPO:-$HOME/osu_megamix}"
LOG_DIR="${LOG_DIR:-$REPO/dryruns}"
BUILD_DIR="${BUILD_DIR:-$REPO/builddir}"

mkdir -p "$LOG_DIR"

stamp() { date "+%Y-%m-%d %H:%M:%S"; }
say() { print -r -- "[$(stamp)] $*"; }

BIN="$BUILD_DIR/osu_megamix"
PY="$BUILD_DIR/osu_megamix.py"
ROOT_PY="$REPO/osu_megamix.py"

run_one() {
  local mode="$1"
  local out="$LOG_DIR/${mode}.log"

  say "=== DRY RUN: mode=$mode ==="
  say "log: $out"

  # Prefer binary if present+executable, else python.
  # NOTE: we DO NOT feed </dev/null so the program can still read stdin if it insists.
  # We'll pipe an empty line to satisfy "press Enter for default" prompts.
  if [[ -x "$BIN" ]]; then
    print -r -- "" | "$BIN" --enable-npc --mode "$mode" >"$out" 2>&1 || true
  elif [[ -f "$PY" ]]; then
    print -r -- "" | python3 "$PY" --enable-npc --mode "$mode" >"$out" 2>&1 || true
  elif [[ -f "$ROOT_PY" ]]; then
    print -r -- "" | python3 "$ROOT_PY" --enable-npc --mode "$mode" >"$out" 2>&1 || true

  else
    say "ERROR: No runnable build found at $BIN or $PY"
    return 2
  fi

  # Hard checks
  if ! grep -q "Session complete" "$out"; then
    say "FAIL: missing 'Session complete' for $mode"
    return 1
  fi

  # Soft checks
  if grep -q "No beatmaps available" "$out"; then
    say "WARN: $mode has no beatmaps available"
  fi

  say "PASS: $mode"
  return 0
}

say "Repo: $REPO"
say "Builddir: $BUILD_DIR"
say "Logs: $LOG_DIR"

MODES=(osu_megamix osu taiko catch mania)

fail=0
for m in $MODES; do
  run_one "$m" || fail=1
done

say "=== SUMMARY ==="
for m in $MODES; do
  f="$LOG_DIR/${m}.log"
  if [[ -f "$f" ]]; then
    print -r -- "  $m -> $f"
  else
    print -r -- "  $m -> (no log)"
    fail=1
  fi
done

exit $fail
