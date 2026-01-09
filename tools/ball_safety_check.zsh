#!/usr/bin/env zsh
set -euo pipefail

die() { print -r -- "BALL SAFETY CHECK FAIL: $*" >&2; exit 1; }

# Must be inside a git repo
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not a git repo"

# Clean working tree required (ball pushes should be intentional and reproducible)
if [[ -n "$(git status --porcelain=v1)" ]]; then
  git status -sb >&2
  die "working tree not clean"
fi

# If repo uses submodules: .gitmodules must exist AND mappings must be valid
if git ls-files -s | awk '{print $1}' | grep -q '^160000$'; then
  [[ -f .gitmodules ]] || die ".gitmodules missing but submodule gitlinks exist"

  # Validate each gitlink path has a mapping entry
  local path
  while read -r path; do
    git config -f .gitmodules --get-regexp '^submodule\..*\.path$' | awk '{print $2}' | grep -qx -- "$path" \
      || die "no submodule mapping in .gitmodules for path '$path'"
  done < <(git ls-files -s | awk '$1=="160000"{print $4}')

  # Ensure submodules are initialized and not dirty
  git submodule update --init --recursive >/dev/null 2>&1 || die "submodule init/update failed"
  local dirty
  dirty="$(git submodule foreach --recursive 'git status --porcelain=v1 | head -n 1' 2>/dev/null | wc -l | tr -d " ")"
  [[ "$dirty" == "0" ]] || die "submodule working tree dirty"
fi

# Ban committing .DS_Store (ball should stay clean)
git ls-files -z | tr '\0' '\n' | grep -qE '(^|/)\.DS_Store$' && die ".DS_Store is tracked"

print -r -- "BALL SAFETY CHECK OK"
