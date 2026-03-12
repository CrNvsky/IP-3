"""tkinter view components for interactive simulation UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from .constants import (
    LOD_LOW_MAX,
    LOD_MEDIUM_MAX,
    MAX_ZOOM,
    MIN_ZOOM,
    REGION_COORDINATES,
    REGION_NAMES,
    REGION_POLYGONS,
    WORLD_HEIGHT,
    WORLD_WIDTH,
    ZOOM_STEP,
)
from .simulation_engine import SimulationSnapshot
from .visuals import metric_to_color, metric_to_green_red


class UIView:
    """Pure UI rendering and widgets."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Game Server Infrastructure Simulation — Iteration 1")
        self.cqi_var = tk.StringVar(value="Global CQI: 0.00")
        self.rooms_var = tk.StringVar(value="Rooms: 0")
        self.selected_info_var = tk.StringVar(value="Select entity for details")
        self._selected_server_id: int | None = None

        self.zoom_factor = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._drag_last: tuple[int, int] | None = None
        self._last_snapshot: SimulationSnapshot | None = None
        self._scale_x = 1.0
        self._scale_y = 1.0

        self._build_layout()
        self._draw_background()

    def bind_start(self, callback: Callable[[], None]) -> None:
        self.start_button.configure(command=callback)

    def bind_stop(self, callback: Callable[[], None]) -> None:
        self.stop_button.configure(command=callback)

    def bind_deploy(self, callback: Callable[[], None]) -> None:
        self.deploy_button.configure(command=callback)

    def bind_toggle_server(self, callback: Callable[[], None]) -> None:
        self.bind_deploy(callback)

    def selected_server_id(self) -> int | None:
        return self._selected_server_id

    def render(self, snapshot: SimulationSnapshot) -> None:
        self._last_snapshot = snapshot
        self._draw_background()
        server_map = {int(server["id"]): server for server in snapshot["servers"]}
        self._draw_connections(snapshot, server_map)
        self._draw_servers(snapshot)
        self._draw_players(snapshot)
        self._draw_lod_labels(snapshot)
        self._update_labels(snapshot)

    def _build_layout(self) -> None:
        self.canvas = tk.Canvas(self.root, width=1080, height=640, bg="#0d1b2a", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_move)
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<Button-1>", self._on_click)

        controls = ttk.Frame(self.root)
        controls.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=8)

        self.start_button = ttk.Button(controls, text="Start")
        self.start_button.pack(side=tk.LEFT, padx=4)

        self.stop_button = ttk.Button(controls, text="Stop")
        self.stop_button.pack(side=tk.LEFT, padx=4)

        self.deploy_button = ttk.Button(controls, text="Toggle Selected Server")
        self.deploy_button.pack(side=tk.LEFT, padx=4)

        ttk.Label(controls, textvariable=self.rooms_var).pack(side=tk.RIGHT, padx=8)
        ttk.Label(controls, textvariable=self.cqi_var).pack(side=tk.RIGHT, padx=8)
        ttk.Label(controls, textvariable=self.selected_info_var).pack(side=tk.LEFT, padx=20)

    def _draw_background(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), fill="#081323", outline="")
        self._draw_region_boundaries()
        self._draw_region_markers()

    def _draw_servers(self, snapshot: SimulationSnapshot) -> None:
        for server in snapshot["servers"]:
            x, y = self._world_to_screen(float(server["x"]), float(server["y"]))
            if not self._is_on_screen(x, y, margin=20):
                continue
            load_ratio = float(server["load_ratio"])
            color = metric_to_green_red(load_ratio)
            outline = "#f8f9fa" if bool(server["is_active"]) else "#495057"
            self.canvas.create_rectangle(x - 5, y - 5, x + 5, y + 5, fill=color, outline=outline, width=1)

    def _draw_players(self, snapshot: SimulationSnapshot) -> None:
        for player in snapshot["players"]:
            x, y = self._world_to_screen(float(player["x"]), float(player["y"]))
            if not self._is_on_screen(x, y, margin=16):
                continue
            color = metric_to_color(1.0 - float(player["latency_score"]))
            size = 2 if self.zoom_factor < LOD_MEDIUM_MAX else 3
            points = [x, y - size, x - size, y + size, x + size, y + size]
            self.canvas.create_polygon(points, fill=color, outline="#f1f3f5")

    def _draw_connections(self, snapshot: SimulationSnapshot, server_map: dict[int, dict[str, float | int | str]]) -> None:
        for player in snapshot["players"]:
            server_id = player["connected_server_id"]
            if server_id is None:
                continue
            server = server_map.get(int(server_id))
            if server is None:
                continue
            px, py = self._world_to_screen(float(player["x"]), float(player["y"]))
            sx, sy = self._world_to_screen(float(server["x"]), float(server["y"]))
            if not self._is_line_visible(px, py, sx, sy):
                continue
            in_room = player["status"] == "in_room"
            self.canvas.create_line(
                px,
                py,
                sx,
                sy,
                fill="#8ecae6" if not in_room else "#2a3f54",
                width=1,
                stipple="gray75" if in_room else "",
            )

    def _draw_lod_labels(self, snapshot: SimulationSnapshot) -> None:
        if self.zoom_factor < LOD_LOW_MAX:
            self._draw_region_labels(snapshot)
            return
        if self.zoom_factor < LOD_MEDIUM_MAX:
            self._draw_server_labels(snapshot)
            return
        self._draw_player_labels(snapshot)

    def _draw_region_labels(self, snapshot: SimulationSnapshot) -> None:
        for region, cqi in snapshot["regional_cqi"].items():
            if region not in REGION_COORDINATES:
                continue
            x, y = self._world_to_screen(*REGION_COORDINATES[region])
            text = f"{REGION_NAMES[region]} CQI:{cqi * 100:.0f}%"
            self.canvas.create_text(x, y - 26, text=text, fill="#f8f9fa", font=("Arial", 10, "bold"))

    def _draw_server_labels(self, snapshot: SimulationSnapshot) -> None:
        for server in snapshot["servers"]:
            if not bool(server["is_active"]):
                continue
            x, y = self._world_to_screen(float(server["x"]), float(server["y"]))
            if not self._is_on_screen(x, y, margin=80):
                continue
            text = (
                f"{server['name']} | rooms:{server['active_rooms']}/{server['max_rooms']} "
                f"| free:{server['free_players']}"
            )
            self.canvas.create_text(x + 14, y - 14, text=text, anchor="w", fill="#e9ecef", font=("Arial", 9))

    def _draw_player_labels(self, snapshot: SimulationSnapshot) -> None:
        for player in snapshot["players"]:
            x, y = self._world_to_screen(float(player["x"]), float(player["y"]))
            if not self._is_on_screen(x, y, margin=100):
                continue
            room_fragment = f"room:{player['room_id']}" if player["room_id"] is not None else "free"
            text = f"#{player['id']} {room_fragment} ping:{player['ping_ms']}ms"
            self.canvas.create_text(x + 10, y - 8, text=text, anchor="w", fill="#dee2e6", font=("Arial", 8))

    def _draw_region_boundaries(self) -> None:
        for polygon in REGION_POLYGONS.values():
            points: list[float] = []
            for x, y in polygon:
                sx, sy = self._world_to_screen(float(x), float(y))
                points.extend([sx, sy])
            self.canvas.create_polygon(points, outline="#495057", fill="#1f513f", width=2)

    def _draw_region_markers(self) -> None:
        for region, (x, y) in REGION_COORDINATES.items():
            sx, sy = self._world_to_screen(float(x), float(y))
            if not self._is_on_screen(sx, sy, margin=40):
                continue
            self.canvas.create_oval(sx - 10, sy - 10, sx + 10, sy + 10, outline="#adb5bd", width=2)
            self.canvas.create_text(sx, sy, text=region, fill="#dee2e6", font=("Arial", 8, "bold"))

    def _on_resize(self, _event: tk.Event[tk.Misc]) -> None:
        self._refresh_scale()
        if self._last_snapshot is not None:
            self.render(self._last_snapshot)

    def _on_pan_start(self, event: tk.Event[tk.Misc]) -> None:
        self._drag_last = (event.x, event.y)

    def _on_pan_move(self, event: tk.Event[tk.Misc]) -> None:
        if self._drag_last is None:
            return
        last_x, last_y = self._drag_last
        self.pan_x += event.x - last_x
        self.pan_y += event.y - last_y
        self._drag_last = (event.x, event.y)
        if self._last_snapshot is not None:
            self.render(self._last_snapshot)

    def _on_zoom(self, event: tk.Event[tk.Misc]) -> None:
        factor = ZOOM_STEP if event.delta > 0 else (1.0 / ZOOM_STEP)
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom_factor * factor))
        cursor_world = self._screen_to_world(event.x, event.y)
        self.zoom_factor = new_zoom
        self._refresh_scale()
        new_screen = self._world_to_screen(*cursor_world)
        self.pan_x += event.x - new_screen[0]
        self.pan_y += event.y - new_screen[1]
        if self._last_snapshot is not None:
            self.render(self._last_snapshot)

    def _on_click(self, event: tk.Event[tk.Misc]) -> None:
        if self._last_snapshot is None:
            return
        world_x, world_y = self._screen_to_world(event.x, event.y)
        info = self._find_nearest_info(world_x, world_y, self._last_snapshot)
        self.selected_info_var.set(info)

    def _find_nearest_info(self, x: float, y: float, snapshot: SimulationSnapshot) -> str:
        best_distance = 1e9
        best_info = "No nearby entity"
        for server in snapshot["servers"]:
            distance = ((float(server["x"]) - x) ** 2 + (float(server["y"]) - y) ** 2) ** 0.5
            if distance < best_distance and distance < 30:
                best_distance = distance
                self._selected_server_id = int(server["id"])
                best_info = (
                    f"Server {server['name']} ({server['region_name']}) "
                    f"rooms:{server['active_rooms']}/{server['max_rooms']} "
                    f"overload:{float(server['load_ratio']) * 100:.0f}% free:{server['free_players']}"
                )
        for player in snapshot["players"]:
            distance = ((float(player["x"]) - x) ** 2 + (float(player["y"]) - y) ** 2) ** 0.5
            if distance < best_distance and distance < 20:
                room_desc = f"room {player['room_id']}" if player["room_id"] is not None else "free"
                best_info = (
                    f"Player #{player['id']} {room_desc} on server {player['connected_server_id']} "
                    f"ping:{player['ping_ms']}ms"
                )
                best_distance = distance
        if best_info == "No nearby entity":
            self._selected_server_id = None
        return best_info

    def _refresh_scale(self) -> None:
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        self._scale_x = (width / WORLD_WIDTH) * self.zoom_factor
        self._scale_y = (height / WORLD_HEIGHT) * self.zoom_factor

    def _world_to_screen(self, world_x: float, world_y: float) -> tuple[float, float]:
        self._refresh_scale()
        return (
            world_x * self._scale_x + self.pan_x,
            world_y * self._scale_y + self.pan_y,
        )

    def _screen_to_world(self, screen_x: float, screen_y: float) -> tuple[float, float]:
        self._refresh_scale()
        return (
            (screen_x - self.pan_x) / self._scale_x,
            (screen_y - self.pan_y) / self._scale_y,
        )

    def _is_on_screen(self, x: float, y: float, margin: float = 0.0) -> bool:
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        return (-margin <= x <= width + margin) and (-margin <= y <= height + margin)

    def _is_line_visible(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        if self._is_on_screen(x1, y1, margin=20) or self._is_on_screen(x2, y2, margin=20):
            return True
        min_x, max_x = sorted((x1, x2))
        min_y, max_y = sorted((y1, y2))
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        return not (max_x < 0 or min_x > width or max_y < 0 or min_y > height)

    def _update_labels(self, snapshot: SimulationSnapshot) -> None:
        self.cqi_var.set(f"Global CQI: {snapshot['global_cqi'] * 100:.1f}%")
        self.rooms_var.set(f"Rooms: {snapshot['rooms']}")
