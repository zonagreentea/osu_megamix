#!/bin/sh
set -eu
echo -n "meta_mode: "
[ -f .meta_mode ] && cat .meta_mode || echo "missing"
echo -n "pre-push hook: "
[ -x .git/hooks/pre-push ] && echo "ON" || echo "OFF"
echo -n "gh shadow present: "
[ -x tools/gh ] && echo "YES (active only if PATH includes ./tools)" || echo "NO"
echo "date: $(date)"
