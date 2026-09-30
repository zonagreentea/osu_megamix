import json
import socket
import time
from typing import Any, Dict, Optional

from .protocol import PROTO_V

def _recvline(sock: socket.socket) -> bytes:
    buf = bytearray()
    while True:
        b = sock.recv(1)
        if not b:
            break
        buf += b
        if b == b"\n":
            break
    return bytes(buf)

def request(host: str, port: int, msg_type: str, data: Dict[str, Any], token: Optional[str] = None, timeout: float = 3.0) -> Dict[str, Any]:
    mid = str(int(time.time() * 1000))
    payload = dict(data)
    if token is not None:
        payload["auth"] = token

    msg = {"v": PROTO_V, "id": mid, "type": msg_type, "data": payload}
    raw = (json.dumps(msg, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

    with socket.create_connection((host, port), timeout=timeout) as s:
        # server sends hello_ack first; read and ignore
        _ = _recvline(s)
        s.sendall(raw)
        line = _recvline(s)
        if not line:
            raise RuntimeError("no response")
        return json.loads(line.decode("utf-8"))
