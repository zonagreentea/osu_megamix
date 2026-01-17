#!/bin/sh
set -e
cd "$(dirname "$0")"
exec python3 -u ./osu_megamix.py "$@"
