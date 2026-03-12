from __future__ import annotations

import unittest

from src.game_server_sim.server_manager import ServerManager


class ServerManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = ServerManager()

    def test_assign_player_to_nearest_active_server(self) -> None:
        self.manager.toggle_region_server("EU", now=0.0)
        self.manager.toggle_region_server("NA", now=0.0)
        player = self.manager.create_player(x=540.0, y=190.0, now=0.0)

        assigned = self.manager.assign_player_to_nearest_server(player, now=0.0)

        self.assertTrue(assigned)
        self.assertIsNotNone(player.connected_server_id)
        self.assertEqual(player.status, "free")
        self.assertGreaterEqual(player.ping_ms, 20)

    def test_room_created_only_on_five_free_players(self) -> None:
        self.manager.toggle_region_server("EU", now=0.0)
        for _ in range(4):
            player = self.manager.create_player(x=545.0, y=192.0, now=0.0)
            self.manager.assign_player_to_nearest_server(player, now=0.0)

        self.manager.create_rooms_from_free_players(now=0.0)
        self.assertEqual(len(self.manager.rooms), 0)

        player = self.manager.create_player(x=545.0, y=192.0, now=0.0)
        self.manager.assign_player_to_nearest_server(player, now=0.0)
        self.manager.create_rooms_from_free_players(now=0.0)
        self.assertEqual(len(self.manager.rooms), 1)

    def test_expire_room_removes_players(self) -> None:
        self.manager.toggle_region_server("EU", now=0.0)
        for _ in range(5):
            player = self.manager.create_player(x=545.0, y=192.0, now=0.0)
            self.manager.assign_player_to_nearest_server(player, now=0.0)
        self.manager.create_rooms_from_free_players(now=0.0)

        self.manager.expire_rooms(now=60.0)

        self.assertEqual(len(self.manager.rooms), 0)
        self.assertEqual(len(self.manager.players), 0)


if __name__ == "__main__":
    unittest.main()
