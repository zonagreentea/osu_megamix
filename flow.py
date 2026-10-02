flow = 100

def up(amount):
    global flow
    flow = min(100, flow + amount)

def down(amount):
    global flow
    flow = max(0, flow - amount)

def busted():
    return flow == 0

def mix():
    return "mix"
