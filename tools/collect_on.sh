#!/bin/sh
set -eu

echo "COLLECT_MODE=ON" > .collect_mode

cat > .git/hooks/pre-push <<'H'
#!/bin/sh
set -eu
while read -r local_ref local_sha remote_ref remote_sha
do
  case "$local_ref" in
    refs/tags/ball-*|refs/heads/*ball*|refs/heads/*Ball*)
      echo "BLOCKED (collect mode): ball stays shadow." >&2
      echo "ref: $local_ref" >&2
      exit 1
      ;;
  esac
done
exit 0
H
chmod +x .git/hooks/pre-push

# optional: shadow gh only if you opt-in by adding ./tools to PATH
cat > tools/gh <<'H'
#!/bin/sh
echo "BLOCKED (collect mode): no releases." >&2
exit 1
H
chmod +x tools/gh

echo "✅ collect mode ON"
