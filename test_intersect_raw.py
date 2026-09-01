from intersect import intersect

# point × point
assert intersect(5, 5)
assert not intersect(5, 6)

# point × duration
assert intersect(5, (0, 10))
assert intersect(0, (0, 10))
assert intersect(10, (0, 10))
assert not intersect(-1, (0, 10))
assert not intersect(11, (0, 10))

# duration × point
assert intersect((0, 10), 5)
assert not intersect((0, 10), 11)

# duration × duration
assert intersect((0, 10), (5, 15))
assert intersect((0, 10), (10, 20))
assert not intersect((0, 10), (11, 20))

print("intersect-raw: PASS")
