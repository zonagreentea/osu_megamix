"""Musical timing, centered windows, and hold-note judgement for osu!megamix."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TimingWindow:
    """A symmetric timing window around an exact musical target."""

    beat_duration: float
    subdivision: int

    @property
    def interval(self) -> float:
        return self.beat_duration / self.subdivision

    @property
    def total(self) -> float:
        return self.interval

    @property
    def early(self) -> float:
        return self.interval / 2

    @property
    def late(self) -> float:
        return self.interval / 2

    def error(self, input_time: float, target_time: float) -> float:
        """Return signed timing error: negative early, positive late."""
        return input_time - target_time

    def contains(self, input_time: float, target_time: float) -> bool:
        """Return whether input lands inside the centered window."""
        return abs(self.error(input_time, target_time)) <= self.interval / 2


@dataclass(frozen=True)
class NoteTiming:
    """One exact musical timing target."""

    target_time: float
    window: TimingWindow

    def judge(self, input_time: float) -> bool:
        return self.window.contains(input_time, self.target_time)


@dataclass(frozen=True)
class HoldTiming:
    """A hold note with independent start and end targets."""

    start: NoteTiming
    end: NoteTiming

    def judge_start(self, input_time: float) -> bool:
        return self.start.judge(input_time)

    def judge_end(self, input_time: float) -> bool:
        return self.end.judge(input_time)

    def duration(self) -> float:
        return self.end.target_time - self.start.target_time


def beat_duration(bpm: float) -> float:
    """Return one beat in seconds."""
    if bpm <= 0:
        raise ValueError("BPM must be greater than zero")
    return 60.0 / bpm


def timing_window(bpm: float, subdivision: int) -> TimingWindow:
    """Create a centered timing window from BPM and subdivision."""
    if subdivision <= 0:
        raise ValueError("subdivision must be greater than zero")
    return TimingWindow(beat_duration(bpm), subdivision)


def note_timing(
    target_time: float,
    bpm: float,
    subdivision: int,
) -> NoteTiming:
    """Create an exact timing target."""
    return NoteTiming(target_time, timing_window(bpm, subdivision))


def hold_timing(
    start_time: float,
    end_time: float,
    bpm: float,
    subdivision: int,
) -> HoldTiming:
    """Create a hold with independent start and end targets."""
    if end_time <= start_time:
        raise ValueError("hold end must be after hold start")

    window = timing_window(bpm, subdivision)

    return HoldTiming(
        start=NoteTiming(start_time, window),
        end=NoteTiming(end_time, window),
    )
