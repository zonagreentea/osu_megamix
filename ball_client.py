#!/usr/bin/env python3
"""Restricted outbound-only ball client.

Protocol: newline-delimited JSON over TCP.
No shell commands, filesystem operations, or listening sockets.
"""
import argparse
import ipaddress
import json
import socket
import sys

ALLOWED = {"ping", "profile", "friends", "requests"}
MAX_RESPONSE = 65536

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=sorted(ALLOWED))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5052)
    parser.add_argument("--node", required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()

    if not args.token.strip() or not args.node.strip():
        parser.error("nonempty node and token required")
    if not 1 <= args.port <= 65535:
        parser.error("invalid port")

    try:
        address = ipaddress.ip_address(args.host)
    except ValueError:
        parser.error("host must be a numeric IP address")

    if not address.is_loopback:
        parser.error(
            "Remote connections disabled until TLS and "
            "server authentication are implemented"
        )

    request = {
        "action": args.action,
        "node": args.node,
        "token": args.token,
    }

    with socket.create_connection(
        (str(address), args.port), timeout=3
    ) as sock:
        sock.settimeout(3)
        sock.sendall(
            json.dumps(request, separators=(",", ":")).encode()
            + b"\n"
        )

        response = bytearray()
        while b"\n" not in response:
            chunk = sock.recv(4096)
            if not chunk:
                raise ConnectionError("server closed connection")
            response.extend(chunk)
            if len(response) > MAX_RESPONSE:
                raise ValueError("response exceeds limit")

    result = json.loads(response.split(b"\n", 1)[0])
    if not isinstance(result, dict):
        raise ValueError("invalid server response")

    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ConnectionError) as exc:
        print(f"ball: {exc}", file=sys.stderr)
        sys.exit(1)
