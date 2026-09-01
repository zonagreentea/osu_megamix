def intersect(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b

    if isinstance(a, (int, float)):
        return b[0] <= a <= b[1]

    if isinstance(b, (int, float)):
        return a[0] <= b <= a[1]

    return a[0] <= b[1] and b[0] <= a[1]
