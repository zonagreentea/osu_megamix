#!/usr/bin/env python3
"""Read-only repository inventory for the ZERO WASTE packaging audit.

Usage: python3 tools/zero_waste_audit.py
Writes nothing; pipe output to a file if desired.
"""
import ast
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", "__pycache__", ".venv", "venv", "node_modules", "dist", "build"}
SOURCE = {".py", ".js", ".html", ".c", ".h", ".zsh", ".sh"}
ASSET = {".png", ".jpg", ".jpeg", ".ogg", ".mp3", ".wav", ".svg", ".ttf", ".otf"}
records = []
for base, dirs, names in os.walk(ROOT):
    dirs[:] = sorted(d for d in dirs if d not in SKIP)
    for name in sorted(names):
        path = Path(base) / name
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(ROOT).as_posix()
        suffix = path.suffix.lower()
        category = ("test" if name.startswith("test_") or "/tests/" in "/" + rel + "/"
                    else "source" if suffix in SOURCE or name == "run"
                    else "asset" if suffix in ASSET else "other")
        entry = {"path": rel, "bytes": path.stat().st_size, "category": category}
        if suffix == ".py":
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.add(node.module.split(".")[0])
                entry["imports"] = sorted(imports)
            except (SyntaxError, UnicodeError, OSError) as exc:
                entry["parse_error"] = type(exc).__name__
        records.append(entry)
print(json.dumps({
    "file_count": len(records),
    "total_bytes": sum(item["bytes"] for item in records),
    "files": records,
}, indent=2))
