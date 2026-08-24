from core.timeline.clock import ClockState, TimelineClock


class FakeClock:
    def __init__(self) -> None:
        self.ns = 0

    def __call__(self) -> int:
        return self.ns

    def advance(self, ns: int) -> None:
        self.ns += ns


def test_clock_is_monotonic():
    source = FakeClock()
    clock = TimelineClock(clock=source)

    clock.start()
    a = clock.now()

    source.advance(1)
    b = clock.now()

    source.advance(999)
    c = clock.now()

    assert a <= b <= c
    assert c == 1_000


def test_smallest_temporal_unit_is_integer_nanosecond():
    source = FakeClock()
    clock = TimelineClock(clock=source)

    clock.start()
    source.advance(1)

    assert clock.now() == 1
    assert isinstance(clock.now(), int)


def test_stop_freezes_timeline_without_blocking_master_clock():
    source = FakeClock()
    clock = TimelineClock(clock=source)

    clock.start()
    source.advance(1_000)
    clock.stop()

    stopped = clock.now()
    source.advance(1_000_000)

    assert clock.now() == stopped
    assert clock.state is ClockState.STOPPED


def test_restart_preserves_continuity():
    source = FakeClock()
    clock = TimelineClock(clock=source)

    clock.start()
    source.advance(10_000)
    clock.stop()

    stopped = clock.now()

    source.advance(50_000)
    clock.start()
    source.advance(5_000)

    assert clock.now() == stopped + 5_000


def test_snapshot_is_immutable_and_generation_changes_on_flow():
    source = FakeClock()
    clock = TimelineClock(clock=source)

    clock.start()
    first = clock.snapshot()

    clock.stop()
    second = clock.snapshot()

    assert first.time_ns == 0
    assert second.time_ns == 0
    assert second.generation > first.generation
