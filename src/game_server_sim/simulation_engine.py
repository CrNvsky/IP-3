"""Simulation engine lifecycle and update loop."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Callable, TypedDict

from .constants import (
    ACTIVE_REGION_SPAWN_PROBABILITY,
    PLAYER_GENERATION_INTERVAL_SECONDS,
    REGION_NAMES,
)
from .performance_manager import PerformanceManager
from .server_manager import ServerManager


class SimulationSnapshot(TypedDict):
    """Read-only data view returned to UI."""

    running: bool
    servers: list[dict[str, float | int | str | bool]]
    players: list[dict[str, float | int | str | None]]
    rooms_data: list[dict[str, int | str | float]]
    rooms: int
    regional_cqi: dict[str, float]
    global_cqi: float


@dataclass
class SimulationEngine:
    """Coordinates simulation updates without UI dependencies."""

    server_manager: ServerManager
    performance_manager: PerformanceManager
    clock: Callable[[], float] = time.time
    running: bool = False
    _last_player_generation_at: float = field(default=0.0)
    _regional_cqi: dict[str, float] = field(default_factory=dict)
    _global_cqi: float = 0.0

    def start(self) -> None:
        """Start simulation loop state."""
        if self.running:
            return
        self.running = True
        self._last_player_generation_at = self.clock()

    def stop(self) -> None:
        """Stop simulation loop state."""
        self.running = False

    def toggle_server(self, region: str) -> None:
        """Toggle preset server for selected region."""
        self.server_manager.toggle_region_server(region, self.clock())
        self._refresh_cqi()

    def toggle_server_by_id(self, server_id: int) -> None:
        """Toggle selected server directly by id."""
        self.server_manager.toggle_server_by_id(server_id, self.clock())
        self._refresh_cqi()

    def tick(self) -> None:
        """Perform one simulation update cycle."""
        if not self.running:
            return
        now = self.clock()
        self._generate_players_if_due(now)
        self.server_manager.process_free_player_timeouts(now)
        self.server_manager.create_rooms_from_free_players(now)
        self.server_manager.expire_rooms(now)
        self._refresh_cqi()

    def snapshot(self) -> SimulationSnapshot:
        """Return a UI-safe snapshot of current state."""
        return {
            "running": self.running,
            "servers": [
                {
                    "id": server.server_id,
                    "name": server.server_name,
                    "region": server.region,
                    "region_name": REGION_NAMES.get(server.region, server.region),
                    "x": server.x,
                    "y": server.y,
                    "is_active": server.is_active,
                    "connected_players": server.connected_players,
                    "free_players": len(server.free_player_ids),
                    "in_room_players": server.in_room_players,
                    "active_rooms": len(server.room_ids),
                    "max_rooms": server.max_rooms,
                    "load_ratio": server.load_ratio(),
                }
                for server in self.server_manager.servers.values()
            ],
            "players": [
                {
                    "id": player.player_id,
                    "x": player.x,
                    "y": player.y,
                    "region": player.region,
                    "connected_server_id": player.connected_server_id,
                    "room_id": player.room_id,
                    "status": player.status,
                    "latency_score": player.latency_score,
                    "ping_ms": player.ping_ms,
                }
                for player in self.server_manager.players.values()
            ],
            "rooms_data": [
                {
                    "id": room.room_id,
                    "key": room.room_key,
                    "server_id": room.server_id,
                    "expires_at": room.expires_at,
                    "players": len(room.player_ids),
                }
                for room in self.server_manager.rooms.values()
            ],
            "rooms": len(self.server_manager.rooms),
            "regional_cqi": dict(self._regional_cqi),
            "global_cqi": self._global_cqi,
        }

    def _generate_players_if_due(self, now: float) -> None:
        elapsed = now - self._last_player_generation_at
        if elapsed < PLAYER_GENERATION_INTERVAL_SECONDS:
            return
        count = int(elapsed // PLAYER_GENERATION_INTERVAL_SECONDS)
        for _ in range(max(1, count)):
            self._create_and_assign_player(now)
        self._last_player_generation_at = now

    def _create_and_assign_player(self, now: float) -> None:
        x, y = self._pick_spawn_point()
        player = self.server_manager.create_player(x=x, y=y, now=now)
        assigned = self.server_manager.assign_player_to_nearest_server(player, now)
        if not assigned:
            self.server_manager.players.pop(player.player_id, None)

    def _pick_spawn_point(self) -> tuple[float, float]:
        active_regions = sorted({s.region for s in self.server_manager.servers.values() if s.is_active})
        use_active_region = bool(active_regions) and random.random() < ACTIVE_REGION_SPAWN_PROBABILITY
        if use_active_region:
            region = random.choice(active_regions)
            return self.server_manager.random_point_in_region(region)
        region = random.choice(list(REGION_NAMES.keys()))
        return self.server_manager.random_point_in_region(region)

    def _refresh_cqi(self) -> None:
        self._regional_cqi = self.performance_manager.calculate_regional_cqi(self.server_manager)
        self._global_cqi = self.performance_manager.calculate_global_cqi(self._regional_cqi)
