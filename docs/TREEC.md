# treec (Clean Tree Snapshot)

Canonical repo snapshot command:

tree -a --dirsfirst -I ".git|.DS_Store|build|builddir|dist|node_modules|.venv|__pycache__|*.egg-info|*.zip|*.tar.gz|*.mp3|*.wav|logs|*.jsonl"

Policy: tree snapshots must show structure + authored files only.
If tree output changes due to caches/build artifacts/binaries, the snapshot is considered unclean.
