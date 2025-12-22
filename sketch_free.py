import os
import subprocess
from datetime import datetime
import shutil

class Logger:
    """Verbose logging with timestamps."""
    @staticmethod
    def log(message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

class GitManager:
    """Handles git operations explicitly."""
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def run_command(self, command: str):
        Logger.log(f"Running command: {command}")
        result = subprocess.run(command, shell=True, cwd=self.repo_path, capture_output=True, text=True)
        Logger.log(f"Output:\n{result.stdout.strip()}")
        if result.stderr.strip():
            Logger.log(f"Errors:\n{result.stderr.strip()}")
        return result

    def full_pull(self):
        Logger.log("Starting full git pull...")
        self.run_command("git fetch --all")
        self.run_command("git reset --hard origin/main")
        Logger.log("Git pull complete.")

    def full_push(self):
        Logger.log("Starting full git push...")
        self.run_command("git add .")
        self.run_command('git commit -m "Full fluff commit" || echo "No changes to commit"')
        self.run_command("git push origin main")
        Logger.log("Git push complete.")

class BuildManager:
    """Handles builds and safe updates from all legacy builds."""
    def __init__(self, build_dir: str, legacy_root: str):
        self.build_dir = build_dir
        self.legacy_root = legacy_root

    def sync_all_legacy_builds(self):
        """Iterate over all legacy builds and copy safely."""
        if not os.path.exists(self.legacy_root):
            Logger.log(f"No legacy builds folder found at {self.legacy_root}, skipping sync.")
            return

        Logger.log(f"Syncing all legacy builds from {self.legacy_root} to {self.build_dir}")
        for legacy_name in os.listdir(self.legacy_root):
            legacy_path = os.path.join(self.legacy_root, legacy_name)
            if os.path.isdir(legacy_path):
                Logger.log(f"Syncing legacy build: {legacy_name}")
                self._copy_folder(legacy_path, self.build_dir)

    def _copy_folder(self, src: str, dst: str):
        for root, dirs, files in os.walk(src):
            rel_path = os.path.relpath(root, src)
            target_dir = os.path.join(dst, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_dir, file)
                shutil.copy2(src_file, dst_file)
                Logger.log(f"Copied {src_file} → {dst_file}")

    def build(self):
        Logger.log(f"Starting build in {self.build_dir}...")
        os.makedirs(self.build_dir, exist_ok=True)
        # Replace with actual build logic
        self._run_build_command("echo 'Compiling project...'")
        Logger.log("Build complete.")

    def _run_build_command(self, command: str):
        Logger.log(f"Executing build command: {command}")
        result = subprocess.run(command, shell=True, cwd=self.build_dir, capture_output=True, text=True)
        Logger.log(f"Build output:\n{result.stdout.strip()}")
        if result.stderr.strip():
            Logger.log(f"Build errors:\n{result.stderr.strip()}")
        return result

class FullFluffWorkflow:
    """Coordinates everything in SEQUOIA MODE, ethically across all builds."""
    def __init__(self, repo_path: str, build_dir: str, legacy_root: str):
        self.git = GitManager(repo_path)
        self.build = BuildManager(build_dir, legacy_root)

    def run(self):
        Logger.log("===== SEQUOIA MODE: FULL-FLUFF WORKFLOW START =====")
        self.git.full_pull()
        self.build.sync_all_legacy_builds()
        self.build.build()
        self.git.full_push()
        Logger.log("===== SEQUOIA MODE: WORKFLOW COMPLETE =====")

if __name__ == "__main__":
    home = os.path.expanduser("~")
    repo_path = os.path.join(home, "full_fluff_workflow_repo")  # your repo
    build_dir = os.path.join(home, "full_fluff_build")          # current build
    legacy_root = os.path.join(home, "full_fluff_legacy_builds") # contains multiple older builds

    # Ensure folders exist
    os.makedirs(repo_path, exist_ok=True)
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(legacy_root, exist_ok=True)

    workflow = FullFluffWorkflow(repo_path, build_dir, legacy_root)
    workflow.run()
