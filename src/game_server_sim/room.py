"""Room entity for simulation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Room:
    """Represents a gameplay room attached to a server."""

    room_id: int
    room_key: str
    server_id: int
    expires_at: float
    player_ids: list[int] = field(default_factory=list)

    def is_expired(self, now: float) -> bool:
        """Return True if this room exceeded its lifetime."""
        return now >= self.expires_at

    def add_player(self, player_id: int, max_players: int) -> bool:
        """Add a player if room has available capacity."""
        if len(self.player_ids) >= max_players:
            return False
        self.player_ids.append(player_id)
        return True
