# osu!megamix

A minimal monotonic clock.

## Model

TIME is continuous.

The nail is now.

The string is the elapsed time between two observations.

## Mathematics

Let:

C(t) = clock reading at time t

For t2 >= t1:

C(t2) >= C(t1)

Elapsed time:

delta = C(t2) - C(t1)

One second:

1 s = 1,000,000,000 ns

Therefore:

seconds = delta / 1,000,000,000

The clock observes time. It does not create, advance, or count time.

## Implementation

    import time

    now = time.monotonic_ns

now() returns a monotonic integer nanosecond reading.

The implementation uses Python's portable monotonic clock interface rather than a platform-specific clock API.

## Test

The initial implementation was tested with:

    a = now()
    time.sleep(0.01)
    b = now()

    assert b >= a
    assert b - a > 0

Result:

    PASS

The test confirmed that the clock advanced over a real elapsed interval and did not move backward during the observation.

The test script was removed after verification.

## Output

A clock reading is an integer number of nanoseconds.

A difference between two readings is the string.

## Principle

Time is not a counter.

The clock observes time.

The nail is now.

The string is elapsed time.
