#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_local_version(path: Path):
    if not path.exists():
        return "0.0.0"
    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return "0.0.0"
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "current_version" in data:
                return str(data["current_version"])
        except json.JSONDecodeError:
            pass
        return text
    except Exception:
        return "0.0.0"


def write_local_version(path: Path, version: str):
    try:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data["current_version"] = version
                    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                    return
            except json.JSONDecodeError:
                pass
        path.write_text(f"{version}\n", encoding="utf-8")
    except Exception as exc:
        print(f"launcher: warning: unable to write version file: {exc}", file=sys.stderr)


def version_key(version: str):
    try:
        return tuple(int(part) for part in str(version).split("."))
    except Exception:
        return (0,)


def verify_signature(data: bytes, signature: str, key: bytes) -> bool:
    expected = hmac.new(key, data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def fetch_json(url: str):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_bytes(url: str):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def candidate_runtime():
    candidates = [
        ROOT / "osu_megamix.py",
        ROOT / "osu_megamix.html",
        ROOT / "osu_megamix_node_test.html",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def launch_target(path: Path):
    if path.suffix == ".py":
        return [sys.executable, str(path)]
    if path.suffix in {".html", ".htm"}:
        return ["./open.zsh", str(path)]
    return [str(path)]


def run_update_gate():
    server = os.environ.get("MEGAMIX_UPDATE_SERVER")
    key = os.environ.get("MEGAMIX_SIGNING_KEY")
    if not server and not key:
        return 0
    if not server or not key:
        print("launcher: signed update requires MEGAMIX_UPDATE_SERVER and MEGAMIX_SIGNING_KEY", file=sys.stderr)
        return 1

    node = os.environ.get("MEGAMIX_NODE_ID", "default-node")
    version_file = ROOT / "VERSION"
    current = read_local_version(version_file)

    try:
        update = fetch_json(f"{server.rstrip('/')}/api/update/check?node={node}")
    except Exception as exc:
        print(f"launcher: update server unreachable: {exc}", file=sys.stderr)
        return 1

    if not update.get("available", False):
        print(f"launcher: no signed update available; local={current}")
        return 0

    remote_version = str(update.get("version", "0.0.0"))
    binary_url = update.get("binary_url")
    signature = update.get("signature")
    if not binary_url or not signature:
        print("launcher: update payload is incomplete", file=sys.stderr)
        return 1

    try:
        payload = fetch_bytes(binary_url)
    except Exception as exc:
        print(f"launcher: failed to download update binary: {exc}", file=sys.stderr)
        return 1

    if not verify_signature(payload, signature, key.encode("utf-8")):
        print("launcher: signature verification failed", file=sys.stderr)
        return 1

    if version_key(remote_version) <= version_key(current):
        write_local_version(version_file, remote_version)
        print(f"launcher: version is already current or newer ({current})")
        return 0

    staged = ROOT / ".signed_update.bin"
    try:
        staged.write_bytes(payload)
        staged.chmod(0o755)
    except Exception as exc:
        print(f"launcher: failed to stage updated binary: {exc}", file=sys.stderr)
        return 1

    write_local_version(version_file, remote_version)
    print(f"launcher: signed update applied: {current} -> {remote_version}")
    return 0


def main():
    if run_update_gate() != 0:
        print("launcher: mandatory signed update check failed; startup blocked.", file=sys.stderr)
        return 1

    runtime = candidate_runtime()
    if runtime is None:
        print("launcher: no runtime target found", file=sys.stderr)
        return 1

    cmd = launch_target(runtime)
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    raise SystemExit(main())
