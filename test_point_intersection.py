from point import point
from intersect import intersect

p0 = point()
p1 = point()

d = (p0, p1)

assert intersect(p0, d)
assert intersect(p1, d)
assert intersect(d, p0)
assert intersect(d, p1)
assert intersect(d, d)

print("point-intersection: PASS")
