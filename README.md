# osu!megamix

A minimal experiment in building a rhythm game from small, composable primitives.

The current architecture deliberately keeps each primitive simple:

```text
timer
  ↓
point
  ↓
duration
  ↓
intersect
  ↓
gameplay
  ↓
score / health
```

## Primitives

### `timer.py`

Provides the authoritative monotonic clock:

```python
import time

now = time.monotonic_ns
```

`now()` returns monotonic nanosecond time.

---

### `point.py`

Creates a point on the timeline:

```python
from timer import now

def point(): return now()
```

A point is simply the current time.

---

### `duration.py`

Creates a temporal interval from a starting point and a length:

```python
```

For example:

```python
(5, 15)
# (5, 15)
```

The representation is simply:

```text
(start, end)
```

---

### `intersect.py`

Tests whether two intervals intersect:

```python
def intersect(a,b): return a[0] <= b[1] and b[0] <= a[1]
```

Examples:

```text
(0, 10) ∩ (5, 15) → True
(0, 4)  ∩ (5, 9)  → False
```

Boundary contact counts as intersection.

The primitive intentionally knows nothing about gameplay, graphics, sliders, or judgement. It only answers:

> Do these two intervals intersect?

---

### `score.py`

Maintains the current score and provides a minimal increment operation:

```python
score = 0

def add():
    global score
    score += 1
```

---

### `health.py`

Represents health as a bounded `0–10` state:

```python
health = max(0, min(10, health + delta))
```

Health is therefore constrained to:

```text
0 ≤ health ≤ 10
```

---

### `test_judgement.py`

Contains the current point-versus-duration judgement tests.

The existing tests verify that points at the beginning, middle, and end of a duration are accepted, while points outside the duration are rejected.

> **Note:** this test currently imports `judgement`, while the current primitive has been renamed to `intersect`. The test file is therefore the next cleanup target.

## Design

The project favors **small primitives over large systems**.

A primitive should answer one question:

```text
timer       → what time is it?
point       → what is this instant?
duration    → what interval does this represent?
intersect   → do these intervals overlap?
score       → how much score do we have?
health      → how much health do we have?
```

Higher-level gameplay can be composed from these primitives later.

### 1D foundation

The game is intentionally being built around a **one-dimensional model**.

Temporal and positional relationships can therefore be represented as intervals on a single axis:

```text
────────────────────────────────────────→

        [────── note ──────]
              [── input ──]

                 ↓

             intersect
                 ↓
                True
```

This keeps the underlying game logic extremely small. More complex objects, such as sliders, can eventually be constructed from these primitives rather than requiring the primitives themselves to understand sliders.

## Current Status

The foundational primitives currently present are:

* `timer.py`
* `point.py`
* `duration.py`
* `intersect.py`
* `score.py`
* `health.py`

The next stage is to connect these primitives into gameplay while preserving the same minimal design.

