import time

_started = time.monotonic_ns()


def now():
    return (time.monotonic_ns() - _started) / 1_000_000_000


def state(value=None):
    return value


def input(value=None):
    return value


def output(value=None):
    return value


def agreement(query):
    return input(query)


def run(value=None):
    return state(value)

