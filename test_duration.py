from point import point

p0 = point()
p1 = point()

d = (p0, p1)

assert len(d) == 2
assert d[0] <= d[1]
assert d[0] == p0
assert d[1] == p1

print("duration: PASS")
