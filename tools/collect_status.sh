#!/bin/sh
set -eu
echo -n "mode: "
[ -f .collect_mode ] && cat .collect_mode || echo "missing"
echo -n "push hook: "
[ -x .git/hooks/pre-push ] && echo "ON" || echo "OFF"
echo -n "gh shadow present: "
[ -x tools/gh ] && echo "YES (active only if PATH includes ./tools)" || echo "NO"
echo "stamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
