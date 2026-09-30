#!/bin/zsh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

: "${REMOTE:=origin}"
: "${BRANCH:=main}"
: "${ARTIFACT_DIR:=dist}"
: "${BUILD_CMD:=}"
: "${TAG_PREFIX:=v}"
: "${ALLOW_DIRTY:=0}"  # set to 1 to skip clean-tree enforcement

die() { print -u2 -- "release_full: $*"; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"; }

need git

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not in a git repo"

HEAD_BRANCH="$(git symbolic-ref -q --short HEAD || true)"
[[ -n "$HEAD_BRANCH" ]] || die "detached HEAD — checkout a branch before releasing"
[[ "$HEAD_BRANCH" == "$BRANCH" ]] || die "on '$HEAD_BRANCH' but expected '$BRANCH' (set BRANCH=... to override)"

if [[ "$ALLOW_DIRTY" != "1" ]] && [[ -n "$(git status --porcelain)" ]]; then
  git status -sb
  die "working tree not clean — commit/stash first (or set ALLOW_DIRTY=1 to override)"
fi

# version/tag
VERSION_FILE=""
if [[ -f VERSION ]]; then VERSION_FILE="VERSION"; fi
if [[ -n "$VERSION_FILE" ]]; then
  VERSION="$(<"$VERSION_FILE")"
  VERSION="${VERSION//$'\n'/}"
else
  VERSION="$(date -u +%Y.%m.%d.%H%M)"
fi

TAG="${TAG_PREFIX}${VERSION}"
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null 2>&1 && die "tag exists: $TAG"

print -- "Releasing $TAG from $BRANCH"

rm -rf "$ARTIFACT_DIR"
mkdir -p "$ARTIFACT_DIR"

if [[ -n "$BUILD_CMD" ]]; then
  print -- "BUILD_CMD: $BUILD_CMD"
  eval "$BUILD_CMD"
else
  print -- "No BUILD_CMD set — skipping build"
fi

git tag -a "$TAG" -m "Release $TAG"

git push "$REMOTE" "$BRANCH"
git push "$REMOTE" "$TAG"

if command -v gh >/dev/null 2>&1; then
  files=()
  if [[ -d "$ARTIFACT_DIR" ]]; then
    while IFS= read -r -d '' f; do files+=("$f"); done < <(find "$ARTIFACT_DIR" -type f -maxdepth 2 -print0)
  fi
  if (( ${#files[@]} > 0 )); then
    gh release create "$TAG" "${files[@]}" --title "$TAG" --notes "Release $TAG"
  else
    gh release create "$TAG" --title "$TAG" --notes "Release $TAG"
  fi
else
  print -- "gh not installed — pushed tag; create release manually if needed."
fi

print -- "✅ Done: $TAG"
