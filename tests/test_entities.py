from __future__ import annotations

import unittest

from src.game_server_sim.constants import ROOM_DURATION_SECONDS
from src.game_server_sim.room import Room
from src.game_server_sim.server import Server


class EntityTests(unittest.TestCase):
    def test_room_expires_after_duration(self) -> None:
        room = Room(room_id=1, room_key="A1B2C3", server_id=1, expires_at=10.0 + ROOM_DURATION_SECONDS)
        self.assertFalse(room.is_expired(10.0 + ROOM_DURATION_SECONDS - 1.0))
        self.assertTrue(room.is_expired(10.0 + ROOM_DURATION_SECONDS))

    def test_server_load_ratio_and_update(self) -> None:
        room = Room(room_id=1, room_key="A1B2C3", server_id=1, expires_at=60.0, player_ids=[1, 2, 3])
        room_2 = Room(room_id=2, room_key="D4E5F6", server_id=1, expires_at=60.0, player_ids=[])
        server = Server(
            server_id=1,
            server_name="EU-1",
            region="EU",
            x=0,
            y=0,
            capacity=10,
            max_rooms=1,
            room_ids=[1],
        )
        server.free_player_ids = [4, 5]
        server.update_counters({1: room, 2: room_2})
        self.assertEqual(server.in_room_players, 3)
        self.assertEqual(server.connected_players, 5)
        self.assertAlmostEqual(server.load_ratio(), 0.0)
        server.attach_room(2)
        self.assertAlmostEqual(server.load_ratio(), 1.0)


if __name__ == "__main__":
    unittest.main()
