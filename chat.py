from moderation import moderator


class Chat:
    def __init__(self):
        self.messages = []

    def send(self, player, message):
        result = moderator.check(player, message)

        if not result.allowed:
            return result

        entry = {
            "player": player,
            "message": message,
        }

        self.messages.append(entry)
        return result

    def history(self):
        return list(self.messages)
