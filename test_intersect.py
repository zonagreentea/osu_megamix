from intersect import intersect

# point ↔ point
assert intersect(5, 5)
assert not intersect(5, 6)

# point ↔ interval
assert intersect(5, (0, 10))
assert intersect(0, (0, 10))
assert intersect(10, (0, 10))
assert not intersect(-1, (0, 10))
assert not intersect(11, (0, 10))

# interval ↔ point
assert intersect((0, 10), 5)
assert not intersect((0, 10), 11)

# interval ↔ interval
assert intersect((0, 10), (5, 15))
assert intersect((5, 15), (0, 10))
assert intersect((0, 10), (10, 20))
assert intersect((10, 20), (0, 10))
assert not intersect((0, 10), (11, 20))

print("intersect: PASS")
