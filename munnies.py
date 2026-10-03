munnies = 0


def acquire(amount):
    global munnies
    munnies += amount
    return munnies


def balance():
    return munnies
