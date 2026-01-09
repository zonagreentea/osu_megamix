#!/usr/bin/env zsh
set -euo pipefail

GREP=/usr/bin/grep
AWK=/usr/bin/awk
WC=/usr/bin/wc

die() { print -r -- "BALL SAFETY CHECK FAIL: $*" >&2; exit 1; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not a git repo"

# Root must be clean
if [[ -n "$(git status --porcelain=v1)" ]]; then
  git status -sb >&2
  die "working tree not clean"
fi

# If gitlinks exist, .gitmodules must exist and contain mappings
if git ls-files -s | $AWK '{print $1}' | $GREP -q '^160000$'; then
  [[ -f .gitmodules ]] || die ".gitmodules missing but submodule gitlinks exist"

  while read -r path; do
    git config -f .gitmodules --get-regexp '\.path$' \
      | $AWK '{print $2}' \
      | $GREP -qx -- "$path" \
      || die "no submodule mapping in .gitmodules for path '$path'"
  done < <(git ls-files -s | $AWK '$1=="160000"{print $4}')
fi

# Ban DS_Store
git ls-files -z | tr '\0' '\n' | $GREP -qE '(^|/)\.DS_Store$' \
  && die ".DS_Store is tracked"

print -r -- "BALL SAFETY CHECK OK"
