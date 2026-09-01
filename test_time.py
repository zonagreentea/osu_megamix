from timer import now
from point import point
from intersect import intersect

p0 = point()
p1 = point()
assert p1 >= p0

d = (p0, p1)
assert d[0] == p0
assert d[1] == p1
assert intersect(p0, d)
assert intersect(p1, d)

print("time: PASS")
