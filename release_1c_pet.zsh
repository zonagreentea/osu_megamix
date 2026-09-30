#!/bin/zsh
set -euo pipefail

# 1c pet release packer
# Output: dist/osu_megamix-1c-pet.mix (tar archive with .mix extension)

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

# Ball must be present to enforce release rules
"$(git rev-parse --show-toplevel)/tools/require_ball.zsh"

# Required files for this release
need=(
  "README.md"
  "tools/require_ball.zsh"
)

for f in "${need[@]}"; do
  [[ -f "$f" ]] || { print -r -- "release: missing required file: $f"; exit 2; }
done

# Make sure the required files are committed (release must be reproducible)
if ! git diff --quiet -- "${need[@]}"; then
  print -r -- "release: working tree has unstaged changes in release files"
  print -r -- "hint: git add/commit README.md + tools/require_ball.zsh first"
  exit 3
fi

if ! git diff --cached --quiet -- "${need[@]}"; then
  print -r -- "release: index has staged-but-uncommitted changes in release files"
  print -r -- "hint: commit first so release is reproducible"
  exit 4
fi

# Identify build stamp from git
short_sha="$(git rev-parse --short HEAD)"
branch="$(git branch --show-current || true)"
ts_utc="$(date -u +"%Y%m%dT%H%M%SZ")"

out_dir="dist"
out_name="osu_megamix-1c-pet.${ts_utc}.${short_sha}.mix"
out_path="${out_dir}/${out_name}"

mkdir -p "$out_dir"

# Optional include: LICENSE if present
files_to_pack=("${need[@]}")
[[ -f "LICENSE" ]] && files_to_pack+=("LICENSE")

# Create tar archive. (No compression: maximally compatible.)
tar -cf "$out_path" -- "${files_to_pack[@]}"

print -r -- "release: wrote $out_path"
print -r -- "meta: branch=${branch:-?} sha=${short_sha} time=${ts_utc}"
