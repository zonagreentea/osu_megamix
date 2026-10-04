import json
import socket
import threading
import uuid

HOST = "127.0.0.1"
PORT = 5050

profiles = {}
friends = {}
pending = {}
lock = threading.Lock()


class Profile:
    def __init__(self, node, name=None):
        self.id = str(uuid.uuid4())
        self.node = node
        self.name = name or node

    def data(self):
        return {
            "id": self.id,
            "node": self.node,
            "name": self.name,
        }


class Connection:
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address
        self.node = None

    def send(self, value):
        self.sock.sendall((json.dumps(value) + "\n").encode())

    def receive(self):
        data = self.sock.recv(4096)
        if not data:
            return None
        return json.loads(data.decode())

    def close(self):
        self.sock.close()


def create_profile(node, name=None):
    with lock:
        if node in profiles:
            return profiles[node]
        profile = Profile(node, name)
        profiles[node] = profile
        friends[node] = set()
        pending[node] = set()
        return profile


def get_profile(node):
    with lock:
        profile = profiles.get(node)
        return profile.data() if profile else None


def update_profile(node, name):
    with lock:
        profile = profiles.get(node)
        if not profile or not name:
            return False
        profile.name = name
        return True


def send_friend_request(source, target):
    with lock:
        if source not in profiles or target not in profiles:
            return False, "profile not found"
        if source == target:
            return False, "cannot friend yourself"
        if target in friends[source]:
            return False, "already friends"
        pending[target].add(source)
        return True, "request sent"


def accept_friend_request(target, source):
    with lock:
        if source not in pending[target]:
            return False, "no pending request"
        pending[target].remove(source)
        friends[target].add(source)
        friends[source].add(target)
        return True, "friends"


def reject_friend_request(target, source):
    with lock:
        if source not in pending[target]:
            return False, "no pending request"
        pending[target].remove(source)
        return True, "request rejected"


def remove_friend(source, target):
    with lock:
        friends[source].discard(target)
        friends[target].discard(source)
        return True, "friend removed"


def list_friends(node):
    with lock:
        return [
            profiles[n].data()
            for n in friends.get(node, set())
            if n in profiles
        ]


def list_requests(node):
    with lock:
        return [
            profiles[n].data()
            for n in pending.get(node, set())
            if n in profiles
        ]


# ---- execution gate ----

ALLOWED_ACTIONS = {
    "profile",
    "update_profile",
    "friend_request",
    "friend_accept",
    "friend_reject",
    "friend_remove",
    "friends",
    "requests",
}


def authorize(node, action):
    with lock:
        return node in profiles and action in ALLOWED_ACTIONS


def execute(node, action, **data):
    if not authorize(node, action):
        return {
            "ok": False,
            "error": "execution denied",
        }

    if action == "profile":
        return {
            "ok": True,
            "profile": get_profile(data.get("node", node)),
        }

    if action == "update_profile":
        name = data.get("name")
        if not name:
            return {"ok": False, "error": "missing name"}
        return {
            "ok": update_profile(node, name),
            "profile": get_profile(node),
        }

    if action == "friend_request":
        ok, message = send_friend_request(
            node,
            data.get("target"),
        )
        return {"ok": ok, "message": message}

    if action == "friend_accept":
        ok, message = accept_friend_request(
            node,
            data.get("source"),
        )
        return {"ok": ok, "message": message}

    if action == "friend_reject":
        ok, message = reject_friend_request(
            node,
            data.get("source"),
        )
        return {"ok": ok, "message": message}

    if action == "friend_remove":
        ok, message = remove_friend(
            node,
            data.get("target"),
        )
        return {"ok": ok, "message": message}

    if action == "friends":
        return {
            "ok": True,
            "friends": list_friends(node),
        }

    if action == "requests":
        return {
            "ok": True,
            "requests": list_requests(node),
        }

    return {
        "ok": False,
        "error": "unknown action",
    }


def connect(host=HOST, port=PORT, node="node", name=None):
    sock = socket.create_connection((host, port))
    connection = Connection(sock, sock.getpeername())

    connection.send({
        "action": "connect",
        "node": node,
        "name": name or node,
    })

    response = connection.receive()

    if not response or not response.get("accepted"):
        connection.close()
        raise ConnectionError("server rejected connection")

    connection.node = node
    return connection


def request(connection, action, **data):
    connection.send({
        "action": action,
        **data,
    })
    return connection.receive()


def handle(connection):
    try:
        hello = connection.receive()

        if not hello or hello.get("action") != "connect":
            connection.send({
                "accepted": False,
                "error": "invalid connection",
            })
            return

        node = hello.get("node")
        name = hello.get("name")

        if not node:
            connection.send({
                "accepted": False,
                "error": "missing node",
            })
            return

        connection.node = node
        profile = create_profile(node, name)

        connection.send({
            "accepted": True,
            "profile": profile.data(),
        })

        while True:
            message = connection.receive()

            if message is None:
                break

            action = message.get("action")

            response = execute(
                node,
                action,
                **{
                    k: v
                    for k, v in message.items()
                    if k != "action"
                },
            )

            connection.send(response)

    except (
        ConnectionResetError,
        BrokenPipeError,
        json.JSONDecodeError,
    ):
        pass

    finally:
        connection.close()


def serve(host=HOST, port=PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()

    print(f"server listening on {host}:{port}")

    while True:
        sock, address = server.accept()
        connection = Connection(sock, address)

        threading.Thread(
            target=handle,
            args=(connection,),
            daemon=True,
        ).start()


def test():
    alice = connect(node="alice", name="Alice")
    bob = connect(node="bob", name="Bob")

    print("\n--- profiles ---")
    print(request(alice, "profile"))
    print(request(bob, "profile"))

    print("\n--- friend request ---")
    print(request(alice, "friend_request", target="bob"))

    print("\n--- Bob requests ---")
    print(request(bob, "requests"))

    print("\n--- accept ---")
    print(request(bob, "friend_accept", source="alice"))

    print("\n--- Alice friends ---")
    print(request(alice, "friends"))

    print("\n--- Bob friends ---")
    print(request(bob, "friends"))

    print("\n--- update profile ---")
    print(request(alice, "update_profile", name="Alice Updated"))

    print("\n--- updated profile ---")
    print(request(alice, "profile"))

    print("\n--- execution gate ---")
    print(request(alice, "not_allowed"))

    alice.close()
    bob.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "server":
        serve()
    else:
        test()
