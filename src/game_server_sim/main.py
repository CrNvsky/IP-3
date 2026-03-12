"""Application entrypoint for Iteration 1."""

from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.game_server_sim.performance_manager import PerformanceManager
    from src.game_server_sim.server_manager import ServerManager
    from src.game_server_sim.simulation_engine import SimulationEngine
    from src.game_server_sim.ui_controller import UIController
else:
    from .performance_manager import PerformanceManager
    from .server_manager import ServerManager
    from .simulation_engine import SimulationEngine
    from .ui_controller import UIController


def build_application() -> tuple[tk.Tk, UIController]:
    """Compose and return tkinter app with controller."""
    root = tk.Tk()
    server_manager = ServerManager()
    performance_manager = PerformanceManager()
    engine = SimulationEngine(server_manager=server_manager, performance_manager=performance_manager)
    controller = UIController(root=root, engine=engine)
    return root, controller


def main() -> None:
    """Run tkinter main loop."""
    root, _controller = build_application()
    root.mainloop()


if __name__ == "__main__":
    main()
