import json
from typing import Any, Dict, Tuple

PROTO_V = "IMAG/1"

def dumps(msg: Dict[str, Any]) -> bytes:
    return (json.dumps(msg, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

def loads(line: bytes) -> Dict[str, Any]:
    obj = json.loads(line.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("message must be a JSON object")
    return obj

def validate(msg: Dict[str, Any]) -> Tuple[str, str, str, Dict[str, Any]]:
    v = msg.get("v")
    mid = msg.get("id")
    mtype = msg.get("type")
    data = msg.get("data", {})
    if v != PROTO_V:
        raise ValueError(f"bad protocol version: {v!r} (expected {PROTO_V})")
    if not isinstance(mid, str) or not mid:
        raise ValueError("id must be a non-empty string")
    if not isinstance(mtype, str) or not mtype:
        raise ValueError("type must be a non-empty string")
    if not isinstance(data, dict):
        raise ValueError("data must be an object")
    return v, mid, mtype, data
