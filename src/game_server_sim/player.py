"""Player entity for simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class Player:
    """Represents a generated player in the simulation."""

    player_id: int
    x: float
    y: float
    region: str
    connected_server_id: int | None = None
    room_id: int | None = None
    status: Literal["free", "in_room"] = "free"
    connected_at: float = 0.0
    last_reassign_at: float = 0.0
    latency_score: float = 1.0
    ping_ms: int = 0

    def connect_server(self, server_id: int, now: float, latency_score: float, ping_ms: int) -> None:
        """Connect player to selected server."""
        self.connected_server_id = server_id
        self.connected_at = now
        self.latency_score = latency_score
        self.ping_ms = ping_ms
        self.status = "free"
        self.room_id = None

    def assign_room(self, room_id: int) -> None:
        """Assign the player to a room."""
        self.room_id = room_id
        self.status = "in_room"

    def clear_assignment(self) -> None:
        """Reset player assignment fields."""
        self.connected_server_id = None
        self.room_id = None
        self.status = "free"
