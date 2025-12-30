import argparse
import asyncio
import time
from typing import Dict, Any, Optional

from .protocol import PROTO_V, dumps, loads, validate

def now_ms() -> int:
    return int(time.time() * 1000)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, token: Optional[str], allow_shutdown: bool):
    peer = writer.get_extra_info("peername")
    async def send(msg: Dict[str, Any]):
        writer.write(dumps(msg))
        await writer.drain()

    async def send_error(req_id: str, code: str, message: str):
        await send({"v": PROTO_V, "id": req_id, "type": "error", "data": {"code": code, "message": message}})

    # greet (server-initiated)
    await send({"v": PROTO_V, "id": "0", "type": "hello_ack", "data": {"ts_ms": now_ms(), "peer": str(peer)}})

    while True:
        line = await reader.readline()
        if not line:
            break

        try:
            msg = loads(line)
            v, mid, mtype, data = validate(msg)

            # auth (optional)
            if token is not None:
                if data.get("auth") != token:
                    await send_error(mid, "auth", "missing/invalid token")
                    continue

            if mtype == "hello":
                await send({"v": PROTO_V, "id": mid, "type": "result", "data": {"ok": True, "caps": ["ping", "run", "event"], "ts_ms": now_ms()}})
            elif mtype == "ping":
                await send({"v": PROTO_V, "id": mid, "type": "pong", "data": {"ts_ms": now_ms()}})
            elif mtype == "run":
                op = data.get("op", "")
                payload = data.get("payload", {})
                if not isinstance(op, str) or not op:
                    await send_error(mid, "bad_request", "run.data.op must be non-empty string")
                    continue
                if not isinstance(payload, dict):
                    await send_error(mid, "bad_request", "run.data.payload must be object")
                    continue

                # minimal ops
                if op == "boot":
                    await send({"v": PROTO_V, "id": mid, "type": "result", "data": {"ok": True, "op": op, "runtime": "imagination*", "v": PROTO_V, "ts_ms": now_ms()}})
                elif op == "status":
                    await send({"v": PROTO_V, "id": mid, "type": "result", "data": {"ok": True, "op": op, "status": "alive", "ts_ms": now_ms()}})
                else:
                    await send_error(mid, "no_such_op", f"unknown op: {op}")
            elif mtype == "event":
                et = data.get("event_type", "")
                payload = data.get("payload", {})
                if not isinstance(et, str) or not et:
                    await send_error(mid, "bad_request", "event.data.event_type must be non-empty string")
                    continue
                if not isinstance(payload, dict):
                    await send_error(mid, "bad_request", "event.data.payload must be object")
                    continue
                # For now: acknowledge + emit back a mirror event
                await send({"v": PROTO_V, "id": mid, "type": "result", "data": {"ok": True, "event_type": et, "ts_ms": now_ms()}})
                await send({"v": PROTO_V, "id": mid, "type": "emit", "data": {"kind": "event_mirror", "event_type": et, "payload": payload, "ts_ms": now_ms()}})
            elif mtype == "shutdown":
                if not allow_shutdown:
                    await send_error(mid, "forbidden", "shutdown not allowed (start server with --allow-shutdown)")
                    continue
                await send({"v": PROTO_V, "id": mid, "type": "result", "data": {"ok": True, "ts_ms": now_ms()}})
                break
            else:
                await send_error(mid, "unknown_type", f"unknown type: {mtype}")

        except Exception as e:
            # If we can't parse id, use "?"
            req_id = "?"
            try:
                if isinstance(msg, dict) and isinstance(msg.get("id"), str):
                    req_id = msg["id"]
            except Exception:
                pass
            await send_error(req_id, "parse", str(e))

    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass

async def run_server(host: str, port: int, token: Optional[str], allow_shutdown: bool):
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, token, allow_shutdown), host, port)
    addrs = ", ".join(str(s.getsockname()) for s in server.sockets or [])
    print(f"[imagination*] IMAG/1 server listening on {addrs} (token={'on' if token else 'off'})")
    async with server:
        await server.serve_forever()

def main(argv=None):
    ap = argparse.ArgumentParser(prog="imagination serve", add_help=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=4444)
    ap.add_argument("--token", default=None, help="Optional shared-secret token required in data.auth")
    ap.add_argument("--allow-shutdown", action="store_true")
    ns = ap.parse_args(argv)
    asyncio.run(run_server(ns.host, ns.port, ns.token, ns.allow_shutdown))
