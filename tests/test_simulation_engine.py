from __future__ import annotations

import unittest

from src.game_server_sim.performance_manager import PerformanceManager
from src.game_server_sim.server_manager import ServerManager
from src.game_server_sim.simulation_engine import SimulationEngine


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class SimulationEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.engine = SimulationEngine(
            server_manager=ServerManager(),
            performance_manager=PerformanceManager(),
            clock=self.clock,
        )

    def test_start_stop_lifecycle(self) -> None:
        self.engine.start()
        self.assertTrue(self.engine.running)
        self.engine.stop()
        self.assertFalse(self.engine.running)

    def test_tick_generates_players_when_running(self) -> None:
        self.engine.toggle_server("EU")
        self.engine.start()

        self.clock.advance(1.1)
        self.engine.tick()

        snapshot = self.engine.snapshot()
        self.assertGreaterEqual(len(snapshot["players"]), 1)
        self.assertGreaterEqual(snapshot["global_cqi"], 0.0)

    def test_room_expires_after_60_seconds(self) -> None:
        self.engine.toggle_server("EU")
        self.engine.start()

        self.clock.advance(5.1)
        self.engine.tick()
        initial_room_ids = set(self.engine.server_manager.rooms.keys())
        self.assertGreaterEqual(len(initial_room_ids), 1)

        self.clock.advance(60.0)
        self.engine.tick()

        remaining_room_ids = set(self.engine.server_manager.rooms.keys())
        self.assertTrue(initial_room_ids.isdisjoint(remaining_room_ids))


if __name__ == "__main__":
    unittest.main()
