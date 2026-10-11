#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import os
import sys


def _read_key(value: str | None) -> bytes:
    if value is not None:
        return value.encode("utf-8")
    env_key = os.environ.get("MEGAMIX_SIGNING_KEY")
    if env_key:
        return env_key.encode("utf-8")
    raise ValueError("No signing key provided. Pass --key or set MEGAMIX_SIGNING_KEY.")


def sign_file(path: str, key: bytes) -> str:
    with open(path, "rb") as handle:
        payload = handle.read()

    digest = hmac.new(key, payload, hashlib.sha256).hexdigest()
    sig_path = path + ".sig"
    with open(sig_path, "w", encoding="utf-8") as handle:
        handle.write(f"sha256={digest}\n")

    print(f"Signed {path} -> {sig_path}")
    return sig_path


def verify_file(path: str, key: bytes) -> bool:
    sig_path = path + ".sig"
    if not os.path.exists(sig_path):
        raise FileNotFoundError(f"Missing signature file for {path}: {sig_path}")

    with open(path, "rb") as handle:
        payload = handle.read()

    expected = hmac.new(key, payload, hashlib.sha256).hexdigest()
    with open(sig_path, "r", encoding="utf-8") as handle:
        sig_text = handle.read().strip()

    if sig_text.startswith("sha256="):
        sig_text = sig_text.split("=", 1)[1]

    if not hmac.compare_digest(expected, sig_text):
        raise ValueError(f"Signature mismatch for {path}")

    print(f"Verified {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign or verify release artifacts with a shared key.")
    parser.add_argument("paths", nargs="*", help="artifact files to sign or verify")
    parser.add_argument("--key", help="shared signing key")
    parser.add_argument("--verify", action="store_true", help="verify an artifact instead of signing it")
    args = parser.parse_args()

    try:
        key = _read_key(args.key)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not args.paths:
        print("No artifact paths supplied.", file=sys.stderr)
        return 2

    try:
        for artifact in args.paths:
            if args.verify:
                verify_file(artifact, key)
            else:
                sign_file(artifact, key)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
