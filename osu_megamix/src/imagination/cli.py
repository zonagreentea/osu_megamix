import argparse
import json
import sys

from .engine.core import run as local_run
from .client import request

def _j(s: str):
    try:
        obj = json.loads(s)
    except Exception as e:
        raise SystemExit(f"bad --json: {e}")
    if not isinstance(obj, dict):
        raise SystemExit("--json must be a JSON object")
    return obj

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    ap = argparse.ArgumentParser(prog="imagination")
    sub = ap.add_subparsers(dest="cmd", required=False)

    ap_local = sub.add_parser("local", help="Run locally (no protocol)")
    ap_local.set_defaults(cmd="local")

    ap_serve = sub.add_parser("serve", help="Run IMAG/1 server")
    ap_serve.add_argument("--host", default="127.0.0.1")
    ap_serve.add_argument("--port", type=int, default=4444)
    ap_serve.add_argument("--token", default=None)
    ap_serve.add_argument("--allow-shutdown", action="store_true")
    ap_serve.set_defaults(cmd="serve")

    ap_ping = sub.add_parser("ping", help="Ping server")
    ap_ping.add_argument("--host", default="127.0.0.1")
    ap_ping.add_argument("--port", type=int, default=4444)
    ap_ping.add_argument("--token", default=None)
    ap_ping.set_defaults(cmd="ping")

    ap_run = sub.add_parser("run", help="Run an op on server")
    ap_run.add_argument("op")
    ap_run.add_argument("--host", default="127.0.0.1")
    ap_run.add_argument("--port", type=int, default=4444)
    ap_run.add_argument("--token", default=None)
    ap_run.add_argument("--json", default="{}")
    ap_run.set_defaults(cmd="run")

    ap_evt = sub.add_parser("event", help="Send an event to server")
    ap_evt.add_argument("event_type")
    ap_evt.add_argument("--host", default="127.0.0.1")
    ap_evt.add_argument("--port", type=int, default=4444)
    ap_evt.add_argument("--token", default=None)
    ap_evt.add_argument("--json", default="{}")
    ap_evt.set_defaults(cmd="event")

    ns = ap.parse_args(argv)

    # default = local run if no cmd
    if ns.cmd is None or ns.cmd == "local":
        local_run()
        return

    if ns.cmd == "serve":
        from .server import main as serve_main
        serve_main(["--host", ns.host, "--port", str(ns.port)] + (["--token", ns.token] if ns.token else []) + (["--allow-shutdown"] if ns.allow_shutdown else []))
        return

    if ns.cmd == "ping":
        resp = request(ns.host, ns.port, "ping", {}, token=ns.token)
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return

    if ns.cmd == "run":
        resp = request(ns.host, ns.port, "run", {"op": ns.op, "payload": _j(ns.json)}, token=ns.token)
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return

    if ns.cmd == "event":
        resp = request(ns.host, ns.port, "event", {"event_type": ns.event_type, "payload": _j(ns.json)}, token=ns.token)
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return
