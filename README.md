# osu!megamix

A minimal experimental game architecture built from small temporal and state primitives.

The current system deliberately favors **variables over constants** and **relationships over abstractions**.

## Primitives

### `timer.py`

Provides the current monotonic clock:

```python
import time

now = time.monotonic_ns
```

`now` is a reference to Python's monotonic nanosecond clock.

### `point.py`

Produces a point in time:

```python
from timer import now

def point():
    return now()
```

A point is an observed value of `now`.

### `duration.py`

Constructs an interval from a starting point and a length:

```python
def duration(time, length):
    return time, time + length
```

The primitive does not impose direction or validate the length.

### `score.py`

Maintains score:

```python
score = 0

def add():
    global score
    score += 1
```

Score is state.

### `health.py`

Represents a bounded health transition:

```python
health = max(0, min(10, health + delta))
```

Health is bounded between `0` and `10`.

The current expression expects `health` and `delta` to exist in its surrounding scope.

## Current Model

The temporal core is intentionally small:

```text
now
 ↓
point
 ↕
duration
```

State exists separately:

```text
score
health
```

The system does not currently contain a dedicated judgement, hit, hold, error, or accuracy primitive.

## What the Tests Show

The primitives have been tested for:

* 10,000 generated points
* monotonic point ordering
* duration reconstruction
* zero-length durations
* reverse durations
* nested durations
* extremely large integer ranges
* arbitrary integer points
* independent score and health state
* temporal composition without judgement logic
* natural Python errors from invalid arguments
* measurement error as the difference between two points
* accuracy as a derived calculation

The temporal stress test passed all tested cases.

Measurement error was represented directly as:

```python
error = actual - target
```

This produced positive, negative, and zero error without requiring an additional primitive.

A tested accuracy relationship was:

```python
accuracy = 1 - abs(error) / duration
```

This produced:

```text
error = 0       → accuracy = 1.0
error = 50      → accuracy = 0.5
error = 100     → accuracy = 0.0
```

The tests also showed that zero duration produces a `ZeroDivisionError`, while negative duration can produce values greater than `1`. These behaviors are currently observed rather than normalized by the architecture.

## Design Direction

The current experiments suggest a simple distinction:

```text
variables
    ↓
relationships
    ↓
derived values
```

A point is a value.

A duration is a relationship describing an interval.

Measurement error is a relationship between two points.

Accuracy is a derived calculation from error and a reference duration.

Consequently, concepts do not automatically become primitives merely because they have names.

The current architecture intentionally avoids adding abstractions until the existing variables and relationships are insufficient.

## Current Files

```text
duration.py
health.py
point.py
score.py
timer.py
README.md
```

The architecture is small by design.

**Whittle the machinery. Don't whittle the concepts.**

