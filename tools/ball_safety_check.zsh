#!/usr/bin/env zsh
set -euo pipefail

GIT=/usr/bin/git
GREP=/usr/bin/grep
AWK=/usr/bin/awk

die() { print -r -- "BALL SAFETY CHECK FAIL: $*" >&2; exit 1; }

$GIT rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not a git repo"

# Root must be clean
if [[ -n "$($GIT status --porcelain=v1)" ]]; then
  $GIT status -sb >&2
  die "working tree not clean"
fi

# If gitlinks exist, .gitmodules must exist and map them
if $GIT ls-files -s | $AWK '{print $1}' | $GREP -q '^160000$'; then
  [[ -f .gitmodules ]] || die ".gitmodules missing but submodule gitlinks exist"

  while read -r path; do
    $GIT config -f .gitmodules --get-regexp '\.path$' \
      | $AWK '{print $2}' \
      | $GREP -qx -- "$path" \
      || die "no submodule mapping in .gitmodules for path '$path'"
  done < <($GIT ls-files -s | $AWK '$1=="160000"{print $4}')
fi

# Ban tracked .DS_Store
$GIT ls-files -z | tr '\0' '\n' | $GREP -qE '(^|/)\.DS_Store$' \
  && die ".DS_Store is tracked"

print -r -- "BALL SAFETY CHECK OK"
