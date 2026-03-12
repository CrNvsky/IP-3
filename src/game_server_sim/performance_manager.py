"""Performance and CQI calculations for simulation."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import OVERLOAD_LOAD_RATIO, WORLD_HEIGHT, WORLD_WIDTH
from .server_manager import ServerManager


@dataclass
class PerformanceManager:
    """Computes regional and global connection quality."""

    max_distance: float = math.hypot(WORLD_WIDTH, WORLD_HEIGHT)

    def calculate_regional_cqi(self, server_manager: ServerManager) -> dict[str, float]:
        """Calculate CQI per region based on active servers."""
        region_servers = self._group_servers_by_region(server_manager)
        regional_cqi: dict[str, float] = {}
        for region, servers in region_servers.items():
            regional_cqi[region] = self._calculate_region_score(servers, server_manager)
        return regional_cqi

    def calculate_global_cqi(self, regional_cqi: dict[str, float]) -> float:
        """Global CQI is the minimum regional CQI."""
        if not regional_cqi:
            return 0.0
        return min(regional_cqi.values())

    def _group_servers_by_region(self, server_manager: ServerManager) -> dict[str, list[int]]:
        grouped: dict[str, list[int]] = {}
        for server in server_manager.servers.values():
            if not server.is_active:
                continue
            grouped.setdefault(server.region, []).append(server.server_id)
        return grouped

    def _calculate_region_score(self, server_ids: list[int], server_manager: ServerManager) -> float:
        if not server_ids:
            return 0.0
        scores = [self._calculate_server_cqi(server_id, server_manager) for server_id in server_ids]
        return sum(scores) / len(scores)

    def _calculate_server_cqi(self, server_id: int, server_manager: ServerManager) -> float:
        server = server_manager.servers[server_id]
        latency_score = self._calculate_latency_score(server_id, server_manager)
        server_stability = self._calculate_server_stability(server.load_ratio())
        return latency_score * server_stability

    def _calculate_latency_score(self, server_id: int, server_manager: ServerManager) -> float:
        server = server_manager.servers[server_id]
        scores: list[float] = []
        for player_id in server.free_player_ids:
            player = server_manager.players.get(player_id)
            if player is not None:
                scores.append(player.latency_score)
        for room_id in server.room_ids:
            room = server_manager.rooms.get(room_id)
            if room is None:
                continue
            for player_id in room.player_ids:
                player = server_manager.players.get(player_id)
                if player is not None:
                    scores.append(player.latency_score)
        if not scores:
            return 1.0
        return sum(scores) / len(scores)

    def _calculate_server_stability(self, load_ratio: float) -> float:
        normalized_load = max(0.0, load_ratio / OVERLOAD_LOAD_RATIO)
        stability = max(0.0, min(1.0, 1.0 - normalized_load))
        return stability
