#!/bin/zsh
set -euo pipefail
set +H 2>/dev/null || true

# OFF = safe, ON = force-with-lease
# usage:
#   ./tools/push_switch.zsh off
#   ./tools/push_switch.zsh on
# then:
#   ./tools/push_switch.zsh push-head
#   ./tools/push_switch.zsh push-main

STATE_FILE=".git/push.switch"

cmd="${1:-}"

case "$cmd" in
  on|off)
    print -r -- "$cmd" > "$STATE_FILE"
    print -r -- "push.switch = $(cat "$STATE_FILE")"
    exit 0
    ;;
  push-head|push-main)
    ;;
  *)
    print -r -- "usage: $0 {on|off|push-head|push-main}" >&2
    exit 2
    ;;
esac

mode="off"
[ -f "$STATE_FILE" ] && mode="$(cat "$STATE_FILE")"

git rev-parse --is-inside-work-tree >/dev/null
git fetch origin

if [[ "$cmd" == "push-head" ]]; then
  # always push your current branch tip
  BALL_PUSH_OK=1 git push -u origin HEAD
  exit 0
fi

# cmd == push-main
git switch main

if [[ "$mode" == "on" ]]; then
  # main follows you (safe force)
  BALL_PUSH_OK=1 git push --force-with-lease origin main
else
  # main is sacred (integrate then push)
  git pull --rebase origin main
  BALL_PUSH_OK=1 git push origin main
fi
