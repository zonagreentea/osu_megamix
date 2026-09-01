from point import point

p0 = point()
p1 = point()

assert p1 >= p0
duration = (p0, p1)

assert duration[0] == p0
assert duration[1] == p1
assert duration[0] <= duration[1]

print("points-as-duration: PASS")
