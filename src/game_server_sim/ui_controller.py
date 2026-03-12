"""UI controller connecting tkinter view with simulation engine."""

from __future__ import annotations

import tkinter as tk

from .constants import SIMULATION_TICK_MS
from .simulation_engine import SimulationEngine
from .ui_view import UIView


class UIController:
    """Binds user actions and schedules real-time updates."""

    def __init__(self, root: tk.Tk, engine: SimulationEngine) -> None:
        self.engine = engine
        self.view = UIView(root)
        self._bind_events()
        self._schedule_loop()

    def _bind_events(self) -> None:
        self.view.bind_start(self.engine.start)
        self.view.bind_stop(self.engine.stop)
        self.view.bind_toggle_server(self._on_toggle_server)

    def _on_toggle_server(self) -> None:
        server_id = self.view.selected_server_id()
        if server_id is None:
            return
        self.engine.toggle_server_by_id(server_id)

    def _schedule_loop(self) -> None:
        self.engine.tick()
        self.view.render(self.engine.snapshot())
        self.view.root.after(SIMULATION_TICK_MS, self._schedule_loop)
