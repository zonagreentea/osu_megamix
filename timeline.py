import time


class Time:
    def __init__(self, value=0):
        self.value = value
        self.children = []

    def add(self, value=0):
        child = Time(value)
        self.children.append(child)
        return child

    def walk(self):
        stack = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))


class Timeline(Time):
    def __init__(self):
        super().__init__(0)
        self.started = time.monotonic_ns()

    def now(self):
        return (time.monotonic_ns() - self.started) / 1_000_000_000
