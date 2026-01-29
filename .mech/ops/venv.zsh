# venv lives inside HUB and is opt-in only
: "${HUB:=$HOME/osu_megamix}"
VENV="$HUB/.venv"

_venv_on(){
  if [[ -f "$VENV/bin/activate" ]]; then source "$VENV/bin/activate"; return 0; fi
  command -v python3 >/dev/null 2>&1 || return 0
  python3 -m venv "$VENV" >/dev/null 2>&1 || return 0
  [[ -f "$VENV/bin/activate" ]] && source "$VENV/bin/activate" || true
}
_venv_off(){ typeset -f deactivate >/dev/null 2>&1 && deactivate || true; }
_venv_status(){ [[ -n "${VIRTUAL_ENV:-}" ]] && echo "VENV=ON ($VIRTUAL_ENV)" || echo "VENV=OFF"; }
