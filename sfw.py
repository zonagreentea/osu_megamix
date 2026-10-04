class SFWPolicy:
    name = "SFW"
    permanent = True

    def allow(self, content):
        return True

    def reject(self, content):
        return False
