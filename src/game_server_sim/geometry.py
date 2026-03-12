"""Geometry helpers for map and region operations."""

from __future__ import annotations

import random


def point_in_polygon(x: float, y: float, polygon: list[tuple[int, int]]) -> bool:
    """Return True when point lies inside a polygon."""
    inside = False
    count = len(polygon)
    j = count - 1
    for i in range(count):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = (yi > y) != (yj > y)
        if intersects:
            slope_x = (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi
            if x < slope_x:
                inside = not inside
        j = i
    return inside


def random_point_within_polygon(polygon: list[tuple[int, int]]) -> tuple[float, float]:
    """Generate random point inside polygon using rejection sampling."""
    xs = [pt[0] for pt in polygon]
    ys = [pt[1] for pt in polygon]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    for _ in range(200):
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        if point_in_polygon(x, y, polygon):
            return x, y
    return float(xs[0]), float(ys[0])
