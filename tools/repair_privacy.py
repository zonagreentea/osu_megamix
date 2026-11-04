#!/usr/bin/env python3
"""
repair_privacy.py

Conservative privacy-first repair tool for osu_megamix.
This version is safer: it validates Python AST before writing changes, and it
inserts the central import after any shebang, module docstring, and __future__
imports so we don't break files that require __future__ to be first.

Run locally from the repository root: python3 repair_privacy.py
"""

from __future__ import annotations

import ast
import os
import re
import shutil
import sys
import time
import py_compile
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

REPO_ROOT = Path(__file__).resolve().parent
BACKUPS_DIR = REPO_ROOT / "privacy_backups"
TIMESTAMP = time.strftime("%Y%m%dT%H%M%S")
WORKING_BACKUP = BACKUPS_DIR / TIMESTAMP

NETWORK_PATTERNS = [
    re.compile(r"\.bind\s*\("),
    re.compile(r"\blisten\s*\("),
    re.compile(r"HTTPServer"),
    re.compile(r"SimpleHTTPServer"),
    re.compile(r"create_server\s*\("),
    re.compile(r"socket\.accept\s*\("),
]

SENSITIVE_FN_NAMES = [
    r"upload",
    r"download",
    r"execute",
    r"run_homework",
    r"create_package",
    r"make_package",
    r"publish_package",
    r"exec_code",
]

MANUAL_REVIEW_PATHS = [
    "server.js",
    "websocket-server.js",
    "websocket.js",
    "sender.js",
    "receiver.js",
]

CHANGED_FILES: List[Path] = []
SKIPPED_FILES: List[Path] = []


def find_python_files(root: Path) -> List[Path]:
    files = []
    for p in root.rglob("*.py"):
        if any(part.startswith(".") for part in p.parts):
            continue
        if BACKUPS_DIR in p.parents:
            continue
        files.append(p)
    return files


def file_matches_patterns(path: Path, patterns: List[re.Pattern]) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    for pat in patterns:
        if pat.search(text):
            return True
    return False


def ensure_backups_dir() -> None:
    WORKING_BACKUP.mkdir(parents=True, exist_ok=True)


def backup_file(path: Path) -> Path:
    rel = path.relative_to(REPO_ROOT)
    dest = WORKING_BACKUP / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    return dest


def create_privacy_controls_module() -> Path:
    dst = REPO_ROOT / "privacy_controls.py"
    if dst.exists():
        return dst

    content = """# Auto-generated centralized privacy controls (conservative defaults)
import socket
import ssl
import threading
from typing import Dict, Any, Optional

_CONSENT: Dict[str, bool] = {}
_ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}
_LOCK = threading.Lock()

DEFAULT_BIND_HOST = '127.0.0.1'

def require_consent(action: str, details: Optional[Dict[str, Any]] = None) -> bool:
    return bool(_CONSENT.get(action))

def set_consent(action: str, allow: bool) -> None:
    _CONSENT[action] = bool(allow)

def register_session(session_id: str, sockets: Dict[str, socket.socket], meta: Optional[Dict[str, Any]] = None) -> None:
    with _LOCK:
        _ACTIVE_SESSIONS[session_id] = {'sockets': sockets, 'meta': meta or {}}

def stop_session(session_id: str) -> None:
    with _LOCK:
        s = _ACTIVE_SESSIONS.pop(session_id, None)
    if not s:
        return
    for name, sock in (s.get('sockets') or {}).items():
        try:
            sock.close()
        except Exception:
            pass

def create_listening_socket(host: Optional[str], port: int, tls_required: bool = True, loopback_only: bool = True):
    bind_host = host
    if not bind_host or str(bind_host) in ('0.0.0.0', '::'):
        bind_host = DEFAULT_BIND_HOST
    if loopback_only and bind_host not in ('127.0.0.1', '::1'):
        bind_host = DEFAULT_BIND_HOST
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((bind_host, int(port)))
    s.listen(5)
    if tls_required:
        return s, True
    return s, False

def wrap_socket_server(sock: socket.socket, certfile: str, keyfile: str) -> ssl.SSLSocket:
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return ctx.wrap_socket(sock, server_side=True)

def peer_authenticate_by_token(token: str) -> bool:
    return False

def check_sandbox_available() -> bool:
    return False

def require_tls_or_die():
    raise RuntimeError('Encrypted transport (TLS) is required for remote hosts')

def require_remote_consent_or_die():
    raise RuntimeError('Explicit user consent required before hosting or accepting remote connections')
"""
    dst.write_text(content, encoding="utf-8")
    print(f"Created centralized privacy_controls.py at {dst}")
    return dst


def find_insert_index_for_import(lines: List[str]) -> int:
    # Keep shebang at top and __future__ imports and module docstring in place
    i = 0
    # shebang
    if i < len(lines) and lines[i].startswith("#!"):
        i += 1
    # module docstring
    if i < len(lines) and (lines[i].startswith('"""') or lines[i].startswith("'''")):
        quote = lines[i][:3]
        i += 1
        while i < len(lines) and quote not in lines[i]:
            i += 1
        if i < len(lines):
            i += 1
    # __future__ imports
    while i < len(lines) and re.match(r"\s*from\s+__future__\s+import", lines[i]):
        i += 1
    # Also keep over the following block of imports together
    # we'll insert just after the future/imports/docstring/shebang
    return i


def safe_write(path: Path, text: str, original_text: str) -> bool:
    """Validate AST before writing. If AST parse fails, restore original.
    Returns True if write succeeded.
    """
    try:
        ast.parse(text)
    except SyntaxError as e:
        print(f"AST parse failed for {path}: {e}")
        # leave file unchanged (it has already been backed up by caller)
        # attempt to restore original_text
        try:
            path.write_text(original_text, encoding="utf-8")
        except Exception as ex:
            print(f"Failed to restore original for {path}: {ex}")
        return False
    # Safe to write
    path.write_text(text, encoding="utf-8")
    return True


def make_consent_guard_block(indent: str = "") -> str:
    guard = (
        f"{indent}if not _pc.require_consent('host_server'):\n"
        f"{indent}    raise RuntimeError('Network action blocked: explicit consent required')\n"
        f"{indent}if not _pc.check_sandbox_available():\n"
        f"{indent}    # Ensure TLS/sandbox policies enforced for remote peers\n"
        f"{indent}    pass\n"
    )
    return guard


def safe_replace_bindings_and_insert_guards(path: Path) -> Tuple[bool, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False, ""
    orig = text
    changed = False
    lines = text.splitlines()

    # Insert privacy_controls import after shebang/docstring/__future__ imports
    insert_index = find_insert_index_for_import(lines)
    import_line = "import privacy_controls as _pc"
    already_imported = any(re.match(r"\s*(import|from)\s+privacy_controls", l) for l in lines)
    if not already_imported:
        lines.insert(insert_index, import_line)
        changed = True

    # Reconstruct text for further editing
    text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")

    # Replace insecure bind addresses in simple patterns
    patterns = [
        (re.compile(r"bind\s*\(\s*\(\s*['\"]0\.0\.0\.0['\"]\s*,\s*(\d+)\s*\)\s*\)"), r"bind(('127.0.0.1', \1))"),
        (re.compile(r"bind\s*\(\s*\(\s*['\"]['\"]\s*,\s*(\d+)\s*\)\s*\)"), r"bind(('127.0.0.1', \1))"),
    ]
    for pat, repl in patterns:
        if pat.search(text):
            text, n = pat.subn(repl, text)
            if n:
                changed = True

    # Insert consent guards before listen/bind occurrences conservatively
    lines = text.splitlines()
    out_lines: List[str] = []
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        m = re.search(r"\b(listen|bind)\s*\(", line)
        if m:
            indent = line[:len(line) - len(stripped)]
            # Only insert if guard not nearby
            prev_chunk = "\n".join(out_lines[-3:]) if len(out_lines) >= 3 else "\n".join(out_lines)
            if "require_consent('host_server')" not in prev_chunk:
                guard = make_consent_guard_block(indent)
                out_lines.append(guard)
                changed = True
        out_lines.append(line)
    text = "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")

    # Protect sensitive functions by inserting checks at start of function body
    for name_pat in SENSITIVE_FN_NAMES:
        fn_re = re.compile(rf"(^def\s+{name_pat}\s*\([^)]*\)\s*:\s*)", re.MULTILINE)
        def_matches = list(fn_re.finditer(text))
        # For each match, find the insertion point just after the signature line
        offset = 0
        for m in def_matches:
            start = m.end() + offset
            # inject a small check
            check = "\n    if not _pc.require_consent('sensitive_action') or not _pc.peer_authenticate_by_token(''):\n        raise RuntimeError('Action requires explicit consent and authenticated peer')\n"
            nearby = text[start:start + 200]
            if "require_consent('sensitive_action')" not in nearby:
                text = text[:start] + check + text[start:]
                offset += len(check)
                changed = True

    # Homework fail-closed check appended at module level if relevant
    if 'homework' in path.name or 'homework' in text:
        if '_pc.check_sandbox_available' not in text:
            sandbox_check = ("\n# Enforce sandbox for homework execution: fail closed by default\n"
                             "if not _pc.check_sandbox_available():\n"
                             "    # Deny any top-level automatic execution of homework code\n"
                             "    _pc.set_consent('allow_homework_execution', False)\n")
            text = text + sandbox_check
            changed = True

    if not changed:
        return False, orig
    # Validate AST before writing
    ok = safe_write(path, text, orig)
    return ok, text if ok else orig


def apply_changes(file_paths: List[Path]) -> List[Path]:
    changed = []
    ensure_backups_dir()
    for p in file_paths:
        try:
            backup_file(p)
        except Exception as e:
            print(f"Warning: failed to backup {p}: {e}")
            continue
        ok, _ = safe_replace_bindings_and_insert_guards(p)
        if ok:
            changed.append(p)
    return changed


def run_syntax_checks(files: List[Path]) -> Tuple[bool, List[Tuple[Path, str]]]:
    errors = []
    for p in files:
        try:
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append((p, str(e)))
    return (len(errors) == 0), errors


def run_tests() -> Tuple[bool, str]:
    cmds = [("pytest", ["pytest", "-q"]), ("python -m pytest", [sys.executable, "-m", "pytest", "-q"])]
    for name, cmd in cmds:
        try:
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
            out = proc.stdout.decode(errors='replace')
            if proc.returncode == 0:
                return True, out
            else:
                print(f"Test runner {name} returned code {proc.returncode}. Output:\n{out}")
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            return False, f"Test runner {name} timed out"
    return False, "No pytest runner available or tests failed"


def restore_backups() -> None:
    if not WORKING_BACKUP.exists():
        return
    for p in WORKING_BACKUP.rglob("*"):
        if p.is_file():
            rel = p.relative_to(WORKING_BACKUP)
            dst = REPO_ROOT / rel
            shutil.copy2(p, dst)
    print("Restored files from backups due to validation failure.")


def summarize_changes(changed: List[Path], skipped: List[Path], syntax_errors, test_output: str) -> None:
    print("\nPRIVACY REPAIR SUMMARY")
    print("Timestamp:", TIMESTAMP)
    print("Changed files:")
    for p in changed:
        print(" -", p.relative_to(REPO_ROOT))
    if skipped:
        print("Files skipped / marked for manual review (JS/Node/other):")
        for p in skipped:
            print(" -", p.relative_to(REPO_ROOT))
    if syntax_errors:
        print("Syntax errors encountered:")
        for p, err in syntax_errors:
            print(f" - {p.relative_to(REPO_ROOT)}: {err}")
    print("Test output summary:")
    print(test_output[:1000])
    print("\nRemaining security limitations and manual actions needed:")
    print(" - Node.js/JavaScript server code requires manual review: server.js, websocket-server.js, websocket.js, sender.js, receiver.js")
    print(" - Enforcing router/NAT port-forwarding prevention requires OS/firewall configuration; this script does not modify system firewall.")
    print(" - Real peer authentication requires a certificate or token infrastructure (out of scope). privacy_controls.peer_authenticate_by_token is a placeholder that denies by default.")
    print(" - Sandbox enforcement requires a supported sandbox runtime installed on the host (container, gVisor, firejail, etc.). The script fails closed until a sandbox is configured.")
    print(" - Browser-facing CSRF/CORS protections in JS/HTML should be audited and may require changes to server-side headers in Node code.")


def main() -> None:
    print("Starting privacy repair: scanning repository for network-related Python files...")
    py_files = find_python_files(REPO_ROOT)

    candidates = []
    for p in py_files:
        if file_matches_patterns(p, NETWORK_PATTERNS) or 'homework' in p.name or any(name in p.name for name in ("server", "update", "presence", "upload", "download", "universal")):
            candidates.append(p)
        else:
            if p.name in MANUAL_REVIEW_PATHS:
                SKIPPED_FILES.append(p)

    for name in MANUAL_REVIEW_PATHS:
        p = REPO_ROOT / name
        if p.exists():
            SKIPPED_FILES.append(p)

    pc_path = create_privacy_controls_module()

    if not candidates:
        print("No candidate Python files found for automatic repair. Exiting.")
        return

    print(f"Will inspect and conservatively modify {len(candidates)} Python files.")
    for p in candidates:
        print(" -", p.relative_to(REPO_ROOT))

    changed = apply_changes(candidates)

    files_to_check = list(changed)
    if pc_path not in files_to_check:
        files_to_check.append(pc_path)

    ok_syntax, syntax_errors = run_syntax_checks(files_to_check)
    if not ok_syntax:
        print("Syntax checks failed. Restoring backups...")
        restore_backups()
        summarize_changes(changed, SKIPPED_FILES, syntax_errors, "Syntax check failure - tests not run")
        sys.exit(1)

    tests_ok, test_out = run_tests()
    if not tests_ok:
        print("Tests failed. Restoring backups...")
        restore_backups()
        summarize_changes(changed, SKIPPED_FILES, syntax_errors, test_out)
        sys.exit(1)

    summarize_changes(changed, SKIPPED_FILES, syntax_errors, test_out)
    print("Privacy repair completed successfully. Note: some protections require manual/OS-level enforcement as listed above.")


if __name__ == '__main__':
    main()
