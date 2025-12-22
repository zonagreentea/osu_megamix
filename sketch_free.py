#!/usr/bin/env python3
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# -----------------------------
# SKETCH-FREE Logging
# -----------------------------
def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [SKETCH-FREE] {msg}")

# -----------------------------
# Run shell commands safely
# -----------------------------
def run(cmd: str, cwd: str = None):
    log(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout.strip():
        log(result.stdout.strip())
    if result.stderr.strip():
        log(result.stderr.strip())
    return result

# -----------------------------
# Sync legacy builds safely
# -----------------------------
def sync_legacy(src_dir: str, dst_dir: str):
    src = Path(src_dir)
    dst = Path(dst_dir)
    if not src.exists():
        log(f"No legacy builds found at {src}, skipping.")
        return

    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        target_dir = dst / rel_path
        os.makedirs(target_dir, exist_ok=True)
        for f in files:
            src_file = Path(root) / f
            dst_file = target_dir / f
            if not dst_file.exists():
                shutil.copy2(src_file, dst_file)
                log(f"Copied legacy file: {src_file} → {dst_file}")
            else:
                log(f"Skipped existing file: {dst_file}")

# -----------------------------
# Main workflow
# -----------------------------
def main():
    home = Path.home()
    repo_dir = home / "full_fluff_workflow_repo"
    build_dir = home / "full_fluff_build"
    legacy_dir = home / "full_fluff_legacy_builds"

    # Ensure directories exist
    os.makedirs(repo_dir, exist_ok=True)
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(legacy_dir, exist_ok=True)

    log("===== SKETCH-FREE FULL-FLUFF WORKFLOW START =====")

    # Git pull latest changes
    run("git fetch --all", cwd=str(repo_dir))
    run("git reset --hard origin/main", cwd=str(repo_dir))

    # Sync legacy builds safely
    sync_legacy(str(legacy_dir), str(build_dir))

    # -----------------------------
    # Placeholder build command
    # Replace with your actual build steps
    # -----------------------------
    run("echo 'Compiling project...'", cwd=str(build_dir))
    # Example: run("make -j8", cwd=str(build_dir))

    # Git commit & push updates
    run("git add .", cwd=str(repo_dir))
    run('git commit -m "SKETCH-FREE update: merged legacy unnecessitations" || echo "No changes to commit"', cwd=str(repo_dir))
    run("git push origin main", cwd=str(repo_dir))

    log("===== SKETCH-FREE FULL-FLUFF WORKFLOW COMPLETE =====")

if __name__ == "__main__":
    main()
