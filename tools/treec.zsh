#!/bin/zsh
exec tree -a --dirsfirst \
  -I ".git|.DS_Store|build|builddir|dist|node_modules|.venv|__pycache__|*.egg-info|logs|*.jsonl|*.zip|*.tar.gz|*.mp3|*.wav" \
  "$@"
