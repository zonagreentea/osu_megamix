"""
homework.py

A minimal, versioned portable project format for osu!megamix.

Format (homework.json):
{
  "name": "Display Name",
  "format_version": 1,
  "entry": "relative/path/to/entry.py",
  "runtime": "python3"
}

A homework package is a zip file with suffix `.homework`. The packer writes
an INTEGRITY file containing a sha256 digest computed deterministically over
all files included (sorted by relative path). The unpacker validates the
integrity and prevents path-traversal by rejecting unsafe archive entries.

This module exposes:
- validate_homework_dir(path) -> (True, None) or (False, "reason")
- pack_homework(src_dir, dest_file)
- unpack_homework(archive_file, dest_dir, verify=True) -> extracted_dir
- load_manifest(path) -> dict

"""
from pathlib import Path
import json
import zipfile
import hashlib
import io
import os
from typing import Tuple

REQUIRED_FIELDS = {"name", "format_version", "entry"}
SUPPORTED_FORMAT_VERSIONS = {1}
INTEGRITY_FILENAME = "INTEGRITY"
MANIFEST_NAME = "homework.json"


def load_manifest(path: Path) -> dict:
    path = Path(path)
    if path.is_dir():
        manifest_path = path / MANIFEST_NAME
    else:
        manifest_path = path
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_safe_archive_name(name: str) -> bool:
    # Prevent absolute paths and path traversal
    p = Path(name)
    if p.is_absolute():
        return False
    for part in p.parts:
        if part == "..":
            return False
    return True


def validate_homework_dir(path: Path) -> Tuple[bool, str]:
    p = Path(path)
    manifest_path = p / MANIFEST_NAME
    if not manifest_path.exists():
        return False, "missing manifest"
    try:
        manifest = load_manifest(manifest_path)
    except Exception as e:
        return False, f"invalid manifest: {e}"
    missing = REQUIRED_FIELDS - set(manifest.keys())
    if missing:
        return False, f"manifest missing fields: {', '.join(sorted(missing))}"
    fmt = manifest.get("format_version")
    if fmt not in SUPPORTED_FORMAT_VERSIONS:
        return False, f"unsupported format_version: {fmt}"
    entry = p / manifest.get("entry")
    if not entry.exists():
        return False, f"entry not found: {manifest.get('entry')}"
    return True, None


def _iter_files(src_dir: Path):
    # yield (relative_path str, absolute Path)
    for root, dirs, files in os.walk(src_dir):
        # skip __pycache__
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            full = Path(root) / fn
            rel = full.relative_to(src_dir)
            yield str(rel).replace(os.path.sep, "/"), full


def pack_homework(src_dir: Path, dest_file: Path) -> None:
    src_dir = Path(src_dir)
    dest_file = Path(dest_file)
    if not src_dir.is_dir():
        raise ValueError("src_dir must be a directory")
    files = sorted(list(_iter_files(src_dir)), key=lambda x: x[0])
    h = hashlib.sha256()
    # compute digest deterministically
    for rel, full in files:
        with open(full, "rb") as fh:
            data = fh.read()
        h.update(rel.encode("utf-8") + b"\0" + data)
    integrity = h.hexdigest()
    # write zip
    with zipfile.ZipFile(dest_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel, full in files:
            zf.write(full, arcname=rel)
        # manifest may already be included; write integrity file
        zf.writestr(INTEGRITY_FILENAME, integrity)


def unpack_homework(archive_file: Path, dest_dir: Path, verify: bool = True) -> Path:
    """Validate and extract an archive without exposing partial contents."""
    from security_homework import unpack_homework as secure_unpack

    return secure_unpack(archive_file, dest_dir, verify=verify)



# CLI helpers
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Homework pack/unpack/validate")
    sub = parser.add_subparsers(dest="cmd")
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("path")
    p_pack = sub.add_parser("pack")
    p_pack.add_argument("src")
    p_pack.add_argument("dest")
    p_unpack = sub.add_parser("unpack")
    p_unpack.add_argument("archive")
    p_unpack.add_argument("dest")
    args = parser.parse_args()
    if args.cmd == "validate":
        ok, reason = validate_homework_dir(Path(args.path))
        if not ok:
            print("INVALID:", reason)
            raise SystemExit(2)
        print("OK")
    elif args.cmd == "pack":
        pack_homework(Path(args.src), Path(args.dest))
        print("packed", args.dest)
    elif args.cmd == "unpack":
        unpack_homework(Path(args.archive), Path(args.dest))
        print("unpacked to", args.dest)
    else:
        parser.print_help()
