from point import point
from intersect import intersect

p0 = point()
p1 = point()

# Represent points as zero-length durations
a = (p0, p0)
b = (p1, p1)

# Two identical points intersect
assert intersect(a, a)

# A point intersects the duration containing it
d = (p0, p1)
assert intersect(a, d)
assert intersect(d, a)
assert intersect(b, d)
assert intersect(d, b)

# Two separated points do not
if p0 != p1:
    assert not intersect(a, b)
    assert not intersect(b, a)

print("intersection-model: PASS")
