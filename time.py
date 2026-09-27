import time

def timestamp(value):
    return time.monotonic_ns(), value
