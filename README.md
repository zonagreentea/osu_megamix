# osu!megamix

A minimal experimental game system built from mathematical primitives.

## Primitives

* `TIME` — returns the time at the instant of call.
* `POINT` — returns its input unchanged.
* `SEGMENT` — returns the length between two points.
* `SHAPE` — returns the number of segments.
* `POLYGON` — returns the number of shapes.

## Definitions

```text
t()       → t
p(x)      → x
s(A, B)   → |B - A|
shape(L)  → |L|
polygon(S) → |S|
```

## Principle

Each primitive has one mathematical responsibility.

Higher-level primitives operate on the structure produced by lower-level primitives.

## Status

Minimal experimental foundation for exploring a game built from time, points, segments, shapes, and polygons.

