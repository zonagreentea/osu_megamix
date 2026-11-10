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
        print(f"signed_update_check: warning: unable to write version file: {exc}", file=sys.stderr)


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


def main():
    parser = argparse.ArgumentParser(description="Mandatory signed update gate for osu!megamix")
    parser.add_argument("--server", default=os.environ.get("MEGAMIX_UPDATE_SERVER"))
    parser.add_argument("--node-id", default=os.environ.get("MEGAMIX_NODE_ID", "default-node"))
    parser.add_argument("--key", default=os.environ.get("MEGAMIX_SIGNING_KEY"))
    parser.add_argument("--version-file", default="VERSION")
    parser.add_argument("--target", default=".signed_update.bin")
    args = parser.parse_args()

    if not args.server:
        print("signed_update_check: MEGAMIX_UPDATE_SERVER is not configured; skipping update gate.", file=sys.stderr)
        return 0
    if not args.key:
        print("signed_update_check: MEGAMIX_SIGNING_KEY is required for mandatory signed updates.", file=sys.stderr)
        return 1

    key = args.key.encode("utf-8")
    version_file = Path(args.version_file)
    current_version = read_local_version(version_file)

    try:
        update = fetch_json(f"{args.server.rstrip('/')}/api/update/check?node={args.node_id}")
    except Exception as exc:
        print(f"signed_update_check: update server unreachable: {exc}", file=sys.stderr)
        return 1

    if not update.get("available", False):
        print(f"signed_update_check: no signed update available. local={current_version}")
        return 0

    remote_version = str(update.get("version", "0.0.0"))
    binary_url = update.get("binary_url")
    signature = update.get("signature")

    if not binary_url or not signature:
        print("signed_update_check: signed update payload is incomplete.", file=sys.stderr)
        return 1

    try:
        payload = fetch_bytes(binary_url)
    except Exception as exc:
        print(f"signed_update_check: binary download failed: {exc}", file=sys.stderr)
        return 1

    if not verify_signature(payload, signature, key):
        print("signed_update_check: signature verification failed.", file=sys.stderr)
        return 1

    if version_key(remote_version) <= version_key(current_version):
        write_local_version(version_file, remote_version)
        print(f"signed_update_check: already current or newer at {current_version}; accepted {remote_version}.")
        return 0

    target = Path(args.target)
    try:
        target.write_bytes(payload)
        target.chmod(0o755)
    except Exception as exc:
        print(f"signed_update_check: failed to stage update binary: {exc}", file=sys.stderr)
        return 1

    write_local_version(version_file, remote_version)
    print(f"signed_update_check: mandatory signed update applied: {current_version} -> {remote_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
