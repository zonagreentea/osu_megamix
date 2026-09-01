from segment import segment
from intersect import intersect
assert intersect(5, segment(0, 10))
assert not intersect(-1, segment(0, 10))
assert not intersect(11, segment(0, 10))
assert intersect(0, segment(0, 10))
assert intersect(10, segment(0, 10))
print("judgement: PASS")
