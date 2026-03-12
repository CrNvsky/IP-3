"""Color and visualization helpers."""

from __future__ import annotations


def metric_to_color(metric_0_1: float) -> str:
    """Map 0..1 metric to blue..red gradient."""
    clamped = max(0.0, min(1.0, metric_0_1))
    red = int(255 * clamped)
    blue = int(255 * (1.0 - clamped))
    green = 40
    return f"#{red:02x}{green:02x}{blue:02x}"


def metric_to_green_red(metric_0_1: float) -> str:
    """Map 0..1 metric to green..red gradient."""
    clamped = max(0.0, min(1.0, metric_0_1))
    red = int(255 * clamped)
    green = int(255 * (1.0 - clamped))
    blue = 40
    return f"#{red:02x}{green:02x}{blue:02x}"
