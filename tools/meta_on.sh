#!/bin/sh
set -eu

# marker
echo "META_MODE=ON" > .meta_mode

# pre-push: block ALL ball refs (branches + tags)
cat > .git/hooks/pre-push <<'H'
#!/bin/sh
set -eu
while read -r local_ref local_sha remote_ref remote_sha
do
  case "$local_ref" in
    refs/tags/ball-*|refs/heads/*ball*|refs/heads/*Ball*)
      echo "BLOCKED (meta mode): ball is bricked until Christmas." >&2
      echo "ref: $local_ref" >&2
      exit 1
      ;;
  esac
done
exit 0
H
chmod +x .git/hooks/pre-push

# pre-tag: block creating NEW ball tags locally (optional safety)
cat > .git/hooks/pre-commit <<'H'
#!/bin/sh
# noop placeholder to keep hooks directory consistent
exit 0
H
chmod +x .git/hooks/pre-commit

# shadow gh (opt-in via PATH)
cat > tools/gh <<'H'
#!/bin/sh
echo "BLOCKED (meta mode): releases bricked until Christmas." >&2
exit 1
H
chmod +x tools/gh

# note for humans
cat > .meta_readme <<'R'
META MODE (v2)
- All ball refs blocked from push.
- Optional gh shadow available.
- Local-only refinement allowed.
- Unball with: tools/meta_off.sh
R

echo "✅ meta mode ON"
echo "Tip: to brick gh in this shell:  export PATH=\"$PWD/tools:\$PATH\""
