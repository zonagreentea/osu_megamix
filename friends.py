"""Friend operations backed by osu!megamix's existing network layer."""

import network


class FriendsService:
    """Use the network module's existing profiles and friend-request rules."""

    def create_profile(self, node, name=None):
        return network.create_profile(node, name).data()

    def profile(self, node):
        return network.get_profile(node)

    def request(self, source, target):
        return network.execute(source, "friend_request", target=target)

    def accept(self, target, source):
        return network.execute(target, "friend_accept", source=source)

    def reject(self, target, source):
        return network.execute(target, "friend_reject", source=source)

    def remove(self, source, target):
        if network.get_profile(target) is None:
            return {"ok": False, "message": "profile not found"}
        return network.execute(source, "friend_remove", target=target)

    def list(self, node):
        return network.execute(node, "friends")

    def requests(self, node):
        return network.execute(node, "requests")


_default = FriendsService()

create_profile = _default.create_profile
profile = _default.profile
request = _default.request
accept = _default.accept
reject = _default.reject
remove = _default.remove
list_friends = _default.list
list_requests = _default.requests
