#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def load_key(key_arg=None):
    key = key_arg or os.environ.get("MEGAMIX_SIGNING_KEY")
    if not key:
        raise ValueError("Missing signing key. Pass --key or set MEGAMIX_SIGNING_KEY.")
    return key.encode("utf-8")


def sign_bytes(data: bytes, key: bytes) -> str:
    return hmac.new(key, data, hashlib.sha256).hexdigest()


def verify_bytes(data: bytes, signature: str, key: bytes) -> bool:
    return hmac.compare_digest(sign_bytes(data, key), signature)


def read_local_version(path: Path) -> str:
    if path.exists():
        try:
            return path.read_text(encoding="utf-8").strip() or "0.0.0"
        except Exception:
            return "0.0.0"
    return "0.0.0"


def write_local_version(path: Path, version: str):
    path.write_text(f"{version}\n", encoding="utf-8")


def fetch_json(url: str):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_bytes(url: str):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main():
    parser = argparse.ArgumentParser(description="Mandatory signed binary updater for osu!megamix")
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--server", required=True)
    parser.add_argument("--binary", default="osu_megamix")
    parser.add_argument("--key", default=None)
    parser.add_argument("--mandatory", action="store_true")
    parser.add_argument("--version-file", default="VERSION")
    args = parser.parse_args()

    try:
        key = load_key(args.key)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    version_path = Path(args.version_file)
    current_version = read_local_version(version_path)
    status_url = f"{args.server.rstrip('/')}/api/update/check?node={args.node_id}"

    try:
        update = fetch_json(status_url)
    except Exception as exc:
        print(f"ERROR: cannot reach update server: {exc}", file=sys.stderr)
        return 1

    if not update.get("available"):
        print(f"No update required. Local version: {current_version}")
        return 0

    remote_version = update.get("version", "unknown")
    binary_url = update.get("binary_url")
    signature = update.get("signature")

    if not binary_url or not signature:
        print("ERROR: update payload is incomplete", file=sys.stderr)
        return 1

    try:
        binary = fetch_bytes(binary_url)
    except Exception as exc:
        print(f"ERROR: could not download binary: {exc}", file=sys.stderr)
        return 1

    if not verify_bytes(binary, signature, key):
        print("ERROR: binary signature verification failed", file=sys.stderr)
        return 1

    target = Path(args.binary)
    backup = target.with_suffix(target.suffix + ".bak") if target.suffix else Path(str(target) + ".bak")

    try:
        if target.exists():
            backup.write_bytes(target.read_bytes())
        target.write_bytes(binary)
        target.chmod(0o755)
        write_local_version(version_path, remote_version)
    except Exception as exc:
        print(f"ERROR: could not install update: {exc}", file=sys.stderr)
        if backup.exists():
            try:
                target.write_bytes(backup.read_bytes())
            except Exception:
                pass
        return 1

    print(f"Mandatory update applied: {current_version} -> {remote_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
