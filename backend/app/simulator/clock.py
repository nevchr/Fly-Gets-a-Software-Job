"""A shared, accelerated San Francisco clock for the scene and hiring schedule."""

from math import floor


TICKS_PER_DAY = 96
START_HOUR = 8
OFFICE_OPENS = 7 * 60
OFFICE_CLOSES = 19 * 60


def day_phase(tick_count: int) -> float:
    return ((tick_count + START_HOUR * 4) % TICKS_PER_DAY) / TICKS_PER_DAY


def clock_minutes(tick_count: int) -> int:
    return round(day_phase(tick_count) * 24 * 60)


def is_daytime(tick_count: int) -> bool:
    minute = clock_minutes(tick_count)
    return OFFICE_OPENS <= minute < OFFICE_CLOSES


def advance_simulated_days(previous: float, previous_tick: int, tick_count: int) -> float:
    """Keep the existing career-day number while changing the day length.

    Older databases used eight ticks per day. Their integer day count is retained;
    the fractional part is aligned to the new clock on the first new tick.
    """
    elapsed_days = floor(previous)
    if day_phase(tick_count) < day_phase(previous_tick):
        elapsed_days += 1
    return round(elapsed_days + day_phase(tick_count), 6)
