#!/bin/sh
set -eu

echo "FAILSAFE=0000" > .collect_mode

# BLOCK ALL PUSHES (absolute)
cat > .git/hooks/pre-push <<'H'
#!/bin/sh
set -eu
echo "BLOCKED (FAILSAFE 0000): full hard ball collect." >&2
exit 1
H
chmod +x .git/hooks/pre-push

# Optional: shadow gh (only active if PATH includes ./tools)
cat > tools/gh <<'H'
#!/bin/sh
echo "BLOCKED (FAILSAFE 0000): no releases." >&2
exit 1
H
chmod +x tools/gh

echo "✅ FAILSAFE 0000 ON"
echo "Tip: to brick gh in this shell too:  export PATH=\"$PWD/tools:\$PATH\""
