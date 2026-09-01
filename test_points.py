from point import point

p0 = point()
p1 = point()

assert isinstance(p0, int)
assert isinstance(p1, int)
assert p1 >= p0
assert point() >= p1

print("points: PASS")
