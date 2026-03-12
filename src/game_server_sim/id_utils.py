"""Identifier helpers for players and rooms."""

from __future__ import annotations

import random
import string


def random_player_id(existing: set[int]) -> int:
    """Generate a random non-repeating six-digit player id."""
    while True:
        candidate = random.randint(100000, 999999)
        if candidate not in existing:
            return candidate


def random_room_key(existing: set[str]) -> str:
    """Generate a random non-repeating six-char room key."""
    alphabet = string.ascii_uppercase + string.digits
    while True:
        candidate = "".join(random.choice(alphabet) for _ in range(6))
        if candidate not in existing:
            return candidate
