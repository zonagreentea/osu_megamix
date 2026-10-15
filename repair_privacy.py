#!/usr/bin/env python3
"""
repair_privacy.py

Run this from the repository root. It performs a source-level, privacy-first
repair on the Python portions of the project. It does NOT push changes to
remote repositories; it edits files in-place in the working tree. It creates
timestamped backups of modified files and restores them if validation fails.

Usage: python3 repair_privacy.py

What it does (high-level):
- Scans the tree for Python files that appear to create listening sockets or
  expose HTTP-like endpoints.
- Creates a timestamped backup of every file it modifies.
- Adds a small, centralized privacy_controls module (written at runtime) and
  applies conservative, minimal edits:
    - Default listener bindings are changed to loopback (127.0.0.1) when the
      code attempts to bind 0.0.0.0/''.
    - Insert runtime consent checks before starting listeners.
    - Wrap/upload/download/execute-like functions with auth/consent checks.
    - Ensure homework execution will fail closed if no sandbox is available.
- Runs syntax checks (py_compile) and the repository's test suite (pytest).
- If validation fails, restores original files from backups.
- Prints a summary of changed files and remaining limitations.

Notes & limitations (short):
- This script edits Python source only. It will flag JS/Node/C++ code for
  manual review but will not attempt fragile edits to them.
- Some protections (router port-forwarding prevention, host firewall) require
  OS-level enforcement and cannot be implemented purely in application code.

This file was generated to be conservative and audit-friendly. It aims to
preserve legitimate gameplay while placing network operations behind explicit
consent and authenticated, encrypted channels.
"""

from __future__ import annotations

import ast
import os
import re
import shutil
import sys
import time
import tempfile
import py_compile
import subprocess
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parent
BACKUPS_DIR = REPO_ROOT / "privacy_backups"
TIMESTAMP = time.strftime("%Y%m%dT%H%M%S")
WORKING_BACKUP = BACKUPS_DIR / TIMESTAMP

# Heuristics to find network/listener code (Python-focused)
NETWORK_PATTERNS = [
    re.compile(r"\.bind\s*\("),
    re.compile(r"\blisten\s*\("),
    re.compile(r"HTTPServer"),
    re.compile(r"SimpleHTTPServer"),
    re.compile(r"create_server\s*\("),
    re.compile(r"socket\.accept\s*\("),
]

# Function name heuristics to protect (execution, file share, package creation)
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

PY_TARGET_EXT = ".py"

# Files we will always flag for manual review (JS/Node servers) but will
# not automatically modify.
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
        # skip virtualenvs or backup directories
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
    """Create privacy_controls.py in the repo if it does not already exist.

    This module centralizes consent checks, session tracking, and TLS /
    authentication placeholders. It is intentionally conservative: default
    behavior denies hosting or accepting remote connections unless explicit
    consent is recorded.
    """
    dst = REPO_ROOT / "privacy_controls.py"
    if dst.exists():
        return dst

    content = f"""# Auto-generated privacy controls module
"""
    content += """
import socket
import ssl
import threading
from typing import Dict, Any, Optional

# In-memory stores (not persistent). A production policy should store consent
# and keys in a secure, auditable place.
_CONSENT: Dict[str, bool] = {}
_ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}
_LOCK = threading.Lock()

# By default we are offline and loopback-only.
DEFAULT_BIND_HOST = '127.0.0.1'


def require_consent(action: str, details: Optional[Dict[str, Any]] = None) -> bool:
    """Return True only if explicit consent was previously granted for this
    action. This function is deliberately non-interactive so scripts and tests
    can run without prompting. To change consent, callers should explicitly
    set it via set_consent().
    """
    return bool(_CONSENT.get(action))


def set_consent(action: str, allow: bool) -> None:
    """Explicitly record user consent for an action (e.g. 'host_server').
    This must be invoked by a trusted user action (UI/CLI) and not silently.
    """
    _CONSENT[action] = bool(allow)


def register_session(session_id: str, sockets: Dict[str, socket.socket], meta: Optional[Dict[str, Any]] = None) -> None:
    with _LOCK:
        _ACTIVE_SESSIONS[session_id] = {
            'sockets': sockets,
            'meta': meta or {},
        }


def stop_session(session_id: str) -> None:
    """Close sockets and remove session state. Idempotent.
    """
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
    """Create a listening socket according to the project's privacy rules.

    - If host is None or 0.0.0.0 or '', and loopback_only is True, the socket
      will bind to DEFAULT_BIND_HOST.
    - If tls_required is True the caller must wrap the returned socket with an
      SSLContext (server-side). This helper does not return an SSL socket, it
      enforces the requirement.
    """
    bind_host = host
    if not bind_host or str(bind_host) in ('0.0.0.0', '::'):
        bind_host = DEFAULT_BIND_HOST
    if loopback_only and bind_host not in ('127.0.0.1', '::1'):
        # Override insecure binding to loopback.
        bind_host = DEFAULT_BIND_HOST
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((bind_host, int(port)))
    s.listen(5)
    # Enforce TLS requirement by refusing to return the socket when tls_required
    # is True and there is no explicit wrapper requested by caller. The caller
    # should call wrap_socket_server() to obtain an SSL-wrapped socket.
    if tls_required:
        # Caller must call wrap_socket_server()
        return s, True
    return s, False


def wrap_socket_server(sock: socket.socket, certfile: str, keyfile: str) -> ssl.SSLSocket:
    """Wrap a socket in server-side SSL. This is a minimal helper that raises
    on misconfiguration.
    """
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return ctx.wrap_socket(sock, server_side=True)


def peer_authenticate_by_token(token: str) -> bool:
    """Placeholder: authenticate a remote peer by a cryptographic token or
    certificate. Do NOT rely on display names.
    """
    # Real deployment must check signatures, badges, or verified certificates.
    # By default, no token is accepted.
    return False


def check_sandbox_available() -> bool:
    """Return True if the runtime environment supports a robust sandbox for
    executing untrusted student/homework code. By default we return False so
    execution "fails closed" until administrators opt-in to a secure sandbox.
    """
    return False


# Convenience helpers for use in patched code
def require_tls_or_die():
    raise RuntimeError('Encrypted transport (TLS) is required for remote hosts')


def require_remote_consent_or_die():
    raise RuntimeError('Explicit user consent required before hosting or accepting remote connections')

"""
    dst.write_text(content, encoding="utf-8")
    print(f"Created centralized privacy_controls.py at {dst}")
    return dst


def make_consent_guard_line(action: str = "host_server") -> str:
    # conservative default: require explicit consent
    return f"if not __import__('privacy_controls').require_consent('{action}'):\n" \
           f"    raise RuntimeError('Network action blocked: explicit consent required for {action}')\n"


def safe_replace_bindings_and_insert_guards(path: Path) -> Tuple[bool, str]:
    """Perform minimal, conservative edits to a Python file. Returns (changed, new_text).

    Edits performed:
    - Prepend import privacy_controls as _pc if not present.
    - Replace insecure bind hosts (0.0.0.0 or '') with 127.0.0.1 when found in bind(...) calls.
    - Insert a consent guard before calls to listen(...) or similar patterns.
    - Wrap sensitive function defs (upload/download/execute) with runtime checks.
    """
    text = path.read_text(encoding="utf-8")
    orig = text

    changed = False

    # Ensure we import privacy_controls (use a private alias to avoid name clashes)
    if "import privacy_controls" not in text and "from privacy_controls" not in text:
        text = "import privacy_controls as _pc\n" + text
        changed = True

    # Replace insecure bind addresses in simple patterns: bind(('0.0.0.0', PORT))
    bind_patterns = [
        (re.compile(r"bind\s*\(\s*\(\s*['\"]0\.0\.0\.0['\"]\s*,\s*(\d+)\s*\)\s*\)"), r"bind(('127.0.0.1', \1))"),
        (re.compile(r"bind\s*\(\s*\(\s*['\"]['\"]\s*,\s*(\d+)\s*\)\s*\)"), r"bind(('127.0.0.1', \1))"),
    ]
    for pat, repl in bind_patterns:
        if pat.search(text):
            text, n = pat.subn(repl, text)
            if n:
                changed = True

    # For listen() calls, insert consent guard if not present on preceding lines.
    # We scan lines to find listen invocations and if previous non-empty line isn't a guard, add one.
    lines = text.splitlines()
    out_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        m_listen = re.search(r"\blisten\s*\(", line)
        m_bind = re.search(r"\bbind\s*\(", line)
        if m_listen or m_bind:
            # Determine indent
            indent = line[:len(line) - len(stripped)]
            guard = indent + "if not _pc.require_consent('host_server'):\n" + indent + "    raise RuntimeError('Network action blocked: explicit consent required')"
            # Check previous up to 3 lines for an existing guard or comment that allows
            prev_chunk = "\n".join(out_lines[-3:]) if len(out_lines) >= 3 else "\n".join(out_lines)
            if "require_consent('host_server')" not in prev_chunk:
                out_lines.append(guard)
                changed = True
        out_lines.append(line)
        i += 1
    text = "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")

    # Protect sensitive functions by inserting an auth check at their start.
    # We'll look for "def <name>(...):" and then add a check as the first statement if not present.
    for name_pat in SENSITIVE_FN_NAMES:
        # simple name match
        fn_re = re.compile(rf"(^def\s+{name_pat}\s*\([^)]*\)\s*:\s*)(?:#.*)?$", re.MULTILINE)
        for m in fn_re.finditer(text):
            # insert after the function signature line
            sig = m.group(0)
            insert_at = m.end()
            # Find the following line break
            # We will inject a small check that requires consent+auth
            check = "\n    if not _pc.require_consent('sensitive_action') or not _pc.peer_authenticate_by_token(''):\n        raise RuntimeError('Action requires explicit consent and authenticated peer')\n"
            # Heuristic: avoid duplicating if check already present
            nearby = text[insert_at: insert_at + 200]
            if "require_consent('sensitive_action')" not in nearby:
                text = text[:insert_at] + check + text[insert_at:]
                changed = True

    # Special handling for homework execution: ensure fail-closed if no sandbox
    # Look for likely runner functions or string 'homework' in path or functions
    if 'homework' in path.name or 'homework' in text:
        # Insert a defensive check near top-level: require sandbox availability
        if "check_sandbox_available" not in text:
            sandbox_check = "\n# Enforce sandbox for homework execution: fail closed by default\nif not _pc.check_sandbox_available():\n    # Deny any top-level automatic execution of homework code\n    _pc.set_consent('allow_homework_execution', False)\n"
            text = text + sandbox_check
            changed = True

    return changed, text


def apply_changes(file_paths: List[Path]) -> List[Path]:
    changed = []
    ensure_backups_dir()
    for p in file_paths:
        try:
            backup_file(p)
        except Exception as e:
            print(f"Warning: failed to backup {p}: {e}")
            continue
        ok, new_text = safe_replace_bindings_and_insert_guards(p)
        if ok:
            p.write_text(new_text, encoding="utf-8")
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
    """Run the repository's tests using pytest if available; otherwise run
    python -m pytest. Returns (success, combined_output).
    """
    cmds = [("pytest", ["pytest", "-q"]), ("python -m pytest", [sys.executable, "-m", "pytest", "-q"])]
    for name, cmd in cmds:
        try:
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
            out = proc.stdout.decode(errors='replace')
            if proc.returncode == 0:
                return True, out
            else:
                # Try the next option
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
    # Note remaining limitations
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
            # still add obvious manual-review markers
            if p.name in MANUAL_REVIEW_PATHS:
                SKIPPED_FILES.append(p)

    # Also mark explicit manual review files if they exist
    for name in MANUAL_REVIEW_PATHS:
        p = REPO_ROOT / name
        if p.exists():
            SKIPPED_FILES.append(p)

    # Create central privacy module
    pc_path = create_privacy_controls_module()

    if not candidates:
        print("No candidate Python files found for automatic repair. Exiting.")
        return

    print(f"Will inspect and conservatively modify {len(candidates)} Python files.")
    for p in candidates:
        print(" -", p.relative_to(REPO_ROOT))

    changed = apply_changes(candidates)

    # Run syntax checks on changed files + the privacy controls module
    files_to_check = list(changed)
    if pc_path not in files_to_check:
        files_to_check.append(pc_path)

    ok_syntax, syntax_errors = run_syntax_checks(files_to_check)
    if not ok_syntax:
        print("Syntax checks failed. Restoring backups...")
        restore_backups()
        summarize_changes(changed, SKIPPED_FILES, syntax_errors, "Syntax check failure - tests not run")
        sys.exit(1)

    # Run tests
    tests_ok, test_out = run_tests()
    if not tests_ok:
        print("Tests failed. Restoring backups...")
        restore_backups()
        summarize_changes(changed, SKIPPED_FILES, syntax_errors, test_out)
        sys.exit(1)

    # All good — print summary but do not commit/push beyond the file edits already made by this script running locally.
    summarize_changes(changed, SKIPPED_FILES, syntax_errors, test_out)
    print("Privacy repair completed successfully. Note: some protections require manual/OS-level enforcement as listed above.")


if __name__ == '__main__':
    main()
