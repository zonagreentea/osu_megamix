# zsh-only operation layer env (no surprises)
unsetopt BANG_HIST 2>/dev/null || true
set +H 2>/dev/null || true

export HUB="${HUB:-$HOME/osu_megamix}"
export MECH_ROOT="${MECH_ROOT:-$HUB/.mech}"
export BALL_DIR="${BALL_DIR:-$HOME/Work/ball}"

# mech bins first
export PATH="$MECH_ROOT/bin:$PATH"
hash -r 2>/dev/null || true
