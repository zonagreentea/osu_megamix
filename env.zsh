# zsh-only op layer: hub is osu!megamix (single root)
unsetopt BANG_HIST 2>/dev/null || true
set +H 2>/dev/null || true

export HUB="$HOME/osu_megamix"
export MECH_ROOT="$HUB/.mech"
export BALL_DIR="${BALL_DIR:-$HOME/Work/ball}"

export PATH="$MECH_ROOT/bin:$PATH"
hash -r 2>/dev/null || true
