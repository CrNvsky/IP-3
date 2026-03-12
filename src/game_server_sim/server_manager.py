"""Server and world-state orchestration for simulation."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass, field

from .constants import (
    CONNECTION_BLOCK_OVERLOAD_RATIO,
    DEFAULT_SERVER_CAPACITY,
    DEFAULT_SERVER_MAX_ROOMS,
    FREE_PLAYER_TIMEOUT_SECONDS,
    MAX_PLAYERS_PER_ROOM,
    PRESET_SERVERS,
    REGION_POLYGONS,
    ROOM_DURATION_SECONDS,
)
from .geometry import point_in_polygon, random_point_within_polygon
from .id_utils import random_player_id, random_room_key
from .player import Player
from .room import Room
from .server import Server


@dataclass
class ServerManager:
    """Manages servers, players, rooms, and assignment logic."""

    servers: dict[int, Server] = field(default_factory=dict)
    rooms: dict[int, Room] = field(default_factory=dict)
    players: dict[int, Player] = field(default_factory=dict)
    _next_room_id: int = 1

    def __post_init__(self) -> None:
        self._load_preset_servers()

    def toggle_region_server(self, region: str, now: float) -> Server | None:
        """Toggle active state for preset region server."""
        candidate = self._first_server_in_region(region)
        if candidate is None:
            return None
        return self.toggle_server_by_id(candidate.server_id, now)

    def toggle_server_by_id(self, server_id: int, now: float) -> Server | None:
        """Toggle active state for a selected server."""
        candidate = self.servers.get(server_id)
        if candidate is None:
            return None
        if candidate.is_active:
            self._deactivate_server(candidate, now)
        else:
            candidate.is_active = True
        self.recalculate_all_server_loads()
        return candidate

    def create_player(self, x: float, y: float, now: float) -> Player:
        """Create and store a generated player."""
        player_id = random_player_id(set(self.players.keys()))
        region = self.resolve_region(x, y)
        player = Player(player_id=player_id, x=x, y=y, region=region)
        player.last_reassign_at = now
        self.players[player.player_id] = player
        return player

    def resolve_region(self, x: float, y: float) -> str:
        """Resolve region code from explicit polygons."""
        for region, polygon in REGION_POLYGONS.items():
            if point_in_polygon(x, y, polygon):
                return region
        return "NA"

    def random_point_in_region(self, region: str) -> tuple[float, float]:
        """Generate a random point inside selected region polygon."""
        polygon = REGION_POLYGONS[region]
        return random_point_within_polygon(polygon)

    def assign_player_to_nearest_server(
        self,
        player: Player,
        now: float,
        exclude_server_ids: Iterable[int] | None = None,
    ) -> bool:
        """Connect player to nearest active server as free player."""
        server = self._find_nearest_server(player.x, player.y, exclude_server_ids)
        if server is None:
            return False
        latency = self._latency_score(player.x, player.y, server.x, server.y)
        ping_ms = self._ping_ms(player.x, player.y, server.x, server.y)
        self._detach_player_from_server(player)
        server.add_free_player(player.player_id)
        player.connect_server(server.server_id, now, latency, ping_ms)
        self.recalculate_all_server_loads()
        return True

    def process_free_player_timeouts(self, now: float) -> None:
        """Reassign players waiting too long in free state."""
        for player in list(self.players.values()):
            if player.status != "free" or player.connected_server_id is None:
                continue
            waited = now - player.connected_at
            if waited < FREE_PLAYER_TIMEOUT_SECONDS:
                continue
            current_server_id = player.connected_server_id
            reassigned = self.assign_player_to_nearest_server(
                player,
                now,
                exclude_server_ids=[current_server_id],
            )
            player.last_reassign_at = now
            if not reassigned:
                player.connected_at = now

    def create_rooms_from_free_players(self, now: float) -> None:
        """Create rooms only when 5 free players are available."""
        room_keys = {room.room_key for room in self.rooms.values()}
        for server in self.servers.values():
            if not server.is_active:
                continue
            while len(server.free_player_ids) >= MAX_PLAYERS_PER_ROOM:
                player_ids = server.free_player_ids[:MAX_PLAYERS_PER_ROOM]
                server.free_player_ids = server.free_player_ids[MAX_PLAYERS_PER_ROOM:]
                room = self._create_room(server.server_id, now, room_keys, player_ids)
                for player_id in player_ids:
                    player = self.players.get(player_id)
                    if player is not None:
                        player.assign_room(room.room_id)
        self.recalculate_all_server_loads()

    def expire_rooms(self, now: float) -> None:
        """Remove expired rooms and associated players."""
        expired_room_ids = [room.room_id for room in self.rooms.values() if room.is_expired(now)]
        for room_id in expired_room_ids:
            self._remove_room_and_players(room_id)
        self.recalculate_all_server_loads()

    def recalculate_all_server_loads(self) -> None:
        """Refresh connected player load for all servers."""
        for server in self.servers.values():
            server.update_counters(self.rooms)

    def _load_preset_servers(self) -> None:
        for payload in PRESET_SERVERS:
            server = Server(
                server_id=int(payload["server_id"]),
                server_name=str(payload["server_name"]),
                region=str(payload["region"]),
                x=float(payload["x"]),
                y=float(payload["y"]),
                capacity=DEFAULT_SERVER_CAPACITY,
                max_rooms=DEFAULT_SERVER_MAX_ROOMS,
            )
            self.servers[server.server_id] = server

    def _first_server_in_region(self, region: str) -> Server | None:
        for server in self.servers.values():
            if server.region == region:
                return server
        return None

    def _deactivate_server(self, server: Server, now: float) -> None:
        server.is_active = False
        all_player_ids = list(server.free_player_ids)
        for room_id in list(server.room_ids):
            room = self.rooms.pop(room_id, None)
            if room is None:
                continue
            all_player_ids.extend(room.player_ids)
        server.room_ids = []
        server.free_player_ids = []
        for player_id in all_player_ids:
            player = self.players.get(player_id)
            if player is None:
                continue
            player.clear_assignment()
            assigned = self.assign_player_to_nearest_server(player, now, [server.server_id])
            if not assigned:
                self.players.pop(player.player_id, None)

    def _find_nearest_server(
        self,
        x: float,
        y: float,
        exclude_server_ids: Iterable[int] | None = None,
    ) -> Server | None:
        excluded = set(exclude_server_ids or [])
        candidates = [
            server
            for server in self.servers.values()
            if server.is_active
            and server.server_id not in excluded
            and server.load_ratio() < CONNECTION_BLOCK_OVERLOAD_RATIO
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda server: self._distance(x, y, server.x, server.y))

    def _create_room(
        self,
        server_id: int,
        now: float,
        room_keys: set[str],
        player_ids: list[int],
    ) -> Room:
        room_key = random_room_key(room_keys)
        room_keys.add(room_key)
        room = Room(
            room_id=self._next_room_id,
            room_key=room_key,
            server_id=server_id,
            expires_at=now + ROOM_DURATION_SECONDS,
            player_ids=list(player_ids),
        )
        self.rooms[room.room_id] = room
        self.servers[server_id].attach_room(room.room_id)
        self._next_room_id += 1
        return room

    def _remove_room_and_players(self, room_id: int) -> None:
        room = self.rooms.pop(room_id, None)
        if room is None:
            return
        server = self.servers.get(room.server_id)
        if server is not None:
            server.detach_room(room.room_id)
        for player_id in room.player_ids:
            self.players.pop(player_id, None)

    def _detach_player_from_server(self, player: Player) -> None:
        if player.connected_server_id is None:
            return
        server = self.servers.get(player.connected_server_id)
        if server is not None:
            server.remove_free_player(player.player_id)

    @staticmethod
    def _distance(x1: float, y1: float, x2: float, y2: float) -> float:
        return math.hypot(x2 - x1, y2 - y1)

    @staticmethod
    def _latency_score(x1: float, y1: float, x2: float, y2: float) -> float:
        distance = math.hypot(x2 - x1, y2 - y1)
        normalized = 1.0 - min(1.0, distance / 2000.0)
        return max(0.0, min(1.0, normalized))

    @staticmethod
    def _ping_ms(x1: float, y1: float, x2: float, y2: float) -> int:
        distance = math.hypot(x2 - x1, y2 - y1)
        ping = 20.0 + (distance * 0.15)
        return int(max(20.0, min(300.0, ping)))
