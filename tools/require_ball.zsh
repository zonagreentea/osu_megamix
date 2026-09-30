#!/bin/zsh
set -euo pipefail

# Ball layer invariant:
# "no ball, no rules"
#
# This guard must be called by any script that enforces rules/safety/invariants.

# What counts as "ball present"?
# 1) Explicit env var BALL=1 (recommended for CI / explicit runs), OR
# 2) A repo marker file .ball/.present (recommended for local/dev), OR
# 3) An executable tool named "ball" on PATH (optional convenience)

repo_root="$(cd -- "${0:A:h}/.." && pwd)"
marker_file="$repo_root/.ball/.present"

if [[ "${BALL:-0}" == "1" ]]; then
  exit 0
fi

if [[ -f "$marker_file" ]]; then
  exit 0
fi

if command -v ball >/dev/null 2>&1; then
  exit 0
fi

print -r -- "BALL ENFORCEMENT: ball is not present."
print -r -- 'Invariant: "no ball, no rules"'
print -r -- "Refusing to enforce anything."
exit 121
