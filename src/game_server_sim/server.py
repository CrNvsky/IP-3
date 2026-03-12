"""Server entity for simulation."""

from __future__ import annotations

from dataclasses import dataclass, field

from .room import Room


@dataclass(slots=True)
class Server:
    """Represents a deployed regional game server."""

    server_id: int
    server_name: str
    region: str
    x: float
    y: float
    capacity: int
    max_rooms: int
    is_active: bool = False
    room_ids: list[int] = field(default_factory=list)
    free_player_ids: list[int] = field(default_factory=list)
    connected_players: int = 0
    in_room_players: int = 0

    def load_ratio(self) -> float:
        """Return overload ratio; rises only after max_rooms is exceeded."""
        if self.max_rooms <= 0:
            return 1.0
        overload_rooms = max(0, len(self.room_ids) - self.max_rooms)
        return overload_rooms / self.max_rooms

    def update_counters(self, rooms: dict[int, Room]) -> None:
        """Recalculate player counters from rooms and free list."""
        total_room_players = 0
        for room_id in self.room_ids:
            room = rooms.get(room_id)
            if room is not None:
                total_room_players += len(room.player_ids)
        self.in_room_players = total_room_players
        self.connected_players = self.in_room_players + len(self.free_player_ids)

    def attach_room(self, room_id: int) -> None:
        """Attach room id to this server."""
        self.room_ids.append(room_id)

    def detach_room(self, room_id: int) -> None:
        """Detach room id from this server."""
        self.room_ids = [existing_id for existing_id in self.room_ids if existing_id != room_id]

    def add_free_player(self, player_id: int) -> None:
        """Add player to server free pool."""
        if player_id not in self.free_player_ids:
            self.free_player_ids.append(player_id)

    def remove_free_player(self, player_id: int) -> None:
        """Remove player from server free pool."""
        self.free_player_ids = [pid for pid in self.free_player_ids if pid != player_id]
