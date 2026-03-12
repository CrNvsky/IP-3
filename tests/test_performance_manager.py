from __future__ import annotations

import unittest

from src.game_server_sim.performance_manager import PerformanceManager
from src.game_server_sim.server_manager import ServerManager


class PerformanceManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = ServerManager()
        self.performance = PerformanceManager()

    def test_global_cqi_is_minimum_regional(self) -> None:
        value = self.performance.calculate_global_cqi({"EU": 0.8, "NA": 0.4, "AS": 0.6})
        self.assertEqual(value, 0.4)

    def test_regional_cqi_with_load_penalty(self) -> None:
        self.manager.toggle_region_server("EU", now=0.0)
        server = next(server for server in self.manager.servers.values() if server.region == "EU" and server.is_active)
        for idx in range(5):
            player = self.manager.create_player(x=server.x, y=server.y, now=float(idx))
            self.manager.assign_player_to_nearest_server(player, now=float(idx))
        self.manager.create_rooms_from_free_players(now=1.0)

        regional = self.performance.calculate_regional_cqi(self.manager)

        self.assertIn("EU", regional)
        self.assertGreaterEqual(regional["EU"], 0.0)
        self.assertLessEqual(regional["EU"], 1.0)


if __name__ == "__main__":
    unittest.main()
