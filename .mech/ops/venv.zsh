# optional venv — NEVER blocks
# usage: mech venv-on / mech venv-off / mech venv-status

: "${HUB:=$HOME/osu_megamix}"
VENV="$HUB/.venv"

_venv_on(){
  if [[ -f "$VENV/bin/activate" ]]; then
    source "$VENV/bin/activate"
    return 0
  fi
  # try to create it if missing
  command -v python3 >/dev/null 2>&1 || return 0
  python3 -m venv "$VENV" >/dev/null 2>&1 || return 0
  [[ -f "$VENV/bin/activate" ]] && source "$VENV/bin/activate" || true
}

_venv_off(){
  # best-effort deactivation
  typeset -f deactivate >/dev/null 2>&1 && deactivate || true
}

_venv_status(){
  if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    echo "VENV=ON ($VIRTUAL_ENV)"
  else
    echo "VENV=OFF"
  fi
}
