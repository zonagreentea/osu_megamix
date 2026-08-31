#!/bin/zsh
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
LAZER="$ROOT/runtime/osu/osu!.app"

if [[ ! -d "$LAZER" ]]; then
    print -u2 "ERROR: embedded osu!lazer not found:"
    print -u2 "  $LAZER"
    exit 1
fi

print "Launching embedded osu!lazer..."
open "$LAZER"
