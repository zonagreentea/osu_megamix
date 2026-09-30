#!/bin/zsh
set -euo pipefail

# Usage:
#   tools/run_zsh_script.zsh path/to/script.zsh
# Refuses to run if script isn't a file or isn't zsh.

script="${1:-}"
[[ -n "$script" && -f "$script" ]] || { print -r -- "usage: $0 path/to/script.zsh"; exit 2; }

head -n 1 "$script" | grep -qE '^#!.*/zsh' || {
  print -r -- "refuse: script must start with a zsh shebang (#!/bin/zsh or #!/usr/bin/env zsh)"
  exit 3
}

chmod +x "$script"
exec "$script"
