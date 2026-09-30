# venv (bash) — opt-in, never blocks
VENV="${HUB:-$HOME/osu_megamix}/.venv"

venv_on() {
  if [ -f "$VENV/bin/activate" ]; then
    # shellcheck disable=SC1090
    . "$VENV/bin/activate"
    return 0
  fi
  command -v python3 >/dev/null 2>&1 || return 0
  python3 -m venv "$VENV" >/dev/null 2>&1 || return 0
  [ -f "$VENV/bin/activate" ] && . "$VENV/bin/activate" || true
}

venv_off() {
  type deactivate >/dev/null 2>&1 && deactivate || true
}

venv_status() {
  if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo "VENV=ON ($VIRTUAL_ENV)"
  else
    echo "VENV=OFF"
  fi
}
