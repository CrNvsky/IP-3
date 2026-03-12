"""Project-wide constants for simulation behavior and UI."""

from __future__ import annotations

ROOM_DURATION_SECONDS = 15.0
MAX_PLAYERS_PER_ROOM = 5
SIMULATION_TICK_MS = 200
PLAYER_GENERATION_INTERVAL_SECONDS = 0.1
FREE_PLAYER_TIMEOUT_SECONDS = 5.0
DEFAULT_SERVER_CAPACITY = 100
DEFAULT_SERVER_MAX_ROOMS = 10
OVERLOAD_LOAD_RATIO = 1.0
CONNECTION_BLOCK_OVERLOAD_RATIO = 2.0
ACTIVE_REGION_SPAWN_PROBABILITY = 0.85

WORLD_WIDTH = 1600
WORLD_HEIGHT = 900

REGION_COORDINATES: dict[str, tuple[int, int]] = {
    "NA": (250, 240),
    "SA": (320, 620),
    "EU": (760, 245),
    "AF": (820, 575),
    "AS": (1170, 300),
    "OC": (1330, 705),
}

REGION_NAMES: dict[str, str] = {
    "NA": "North America",
    "SA": "South America",
    "EU": "Europe",
    "AF": "Africa",
    "AS": "Asia",
    "OC": "Oceania",
}

REGION_POLYGONS: dict[str, list[tuple[int, int]]] = {
    "NA": [(80, 120), (360, 95), (470, 250), (390, 405), (150, 395), (55, 245)],
    "SA": [(185, 390), (425, 405), (505, 585), (420, 850), (235, 885), (165, 690)],
    "EU": [(520, 110), (950, 95), (1040, 230), (980, 365), (640, 390), (490, 250)],
    "AF": [(690, 390), (930, 385), (995, 560), (940, 780), (760, 790), (650, 585)],
    "AS": [(980, 150), (1360, 135), (1460, 300), (1405, 470), (1095, 485), (960, 320)],
    "OC": [(1180, 585), (1460, 585), (1510, 760), (1360, 845), (1140, 775)],
}

PRESET_SERVERS: tuple[dict[str, int | str], ...] = (
    {"server_id": 1, "server_name": "NA-1", "region": "NA", "x": 185, "y": 190},
    {"server_id": 2, "server_name": "NA-2", "region": "NA", "x": 285, "y": 255},
    {"server_id": 3, "server_name": "NA-3", "region": "NA", "x": 360, "y": 185},
    {"server_id": 4, "server_name": "NA-4", "region": "NA", "x": 220, "y": 320},
    {"server_id": 5, "server_name": "NA-5", "region": "NA", "x": 340, "y": 305},
    {"server_id": 6, "server_name": "SA-1", "region": "SA", "x": 250, "y": 520},
    {"server_id": 7, "server_name": "SA-2", "region": "SA", "x": 335, "y": 640},
    {"server_id": 8, "server_name": "SA-3", "region": "SA", "x": 295, "y": 760},
    {"server_id": 9, "server_name": "SA-4", "region": "SA", "x": 390, "y": 540},
    {"server_id": 10, "server_name": "SA-5", "region": "SA", "x": 360, "y": 725},
    {"server_id": 11, "server_name": "EU-1", "region": "EU", "x": 640, "y": 210},
    {"server_id": 12, "server_name": "EU-2", "region": "EU", "x": 760, "y": 260},
    {"server_id": 13, "server_name": "EU-3", "region": "EU", "x": 900, "y": 220},
    {"server_id": 14, "server_name": "EU-4", "region": "EU", "x": 700, "y": 320},
    {"server_id": 15, "server_name": "EU-5", "region": "EU", "x": 860, "y": 305},
    {"server_id": 16, "server_name": "AF-1", "region": "AF", "x": 750, "y": 500},
    {"server_id": 17, "server_name": "AF-2", "region": "AF", "x": 840, "y": 610},
    {"server_id": 18, "server_name": "AF-3", "region": "AF", "x": 905, "y": 530},
    {"server_id": 19, "server_name": "AF-4", "region": "AF", "x": 790, "y": 700},
    {"server_id": 20, "server_name": "AF-5", "region": "AF", "x": 900, "y": 690},
    {"server_id": 21, "server_name": "AS-1", "region": "AS", "x": 1080, "y": 230},
    {"server_id": 22, "server_name": "AS-2", "region": "AS", "x": 1180, "y": 310},
    {"server_id": 23, "server_name": "AS-3", "region": "AS", "x": 1320, "y": 260},
    {"server_id": 24, "server_name": "AS-4", "region": "AS", "x": 1130, "y": 420},
    {"server_id": 25, "server_name": "AS-5", "region": "AS", "x": 1280, "y": 390},
    {"server_id": 26, "server_name": "OC-1", "region": "OC", "x": 1235, "y": 665},
    {"server_id": 27, "server_name": "OC-2", "region": "OC", "x": 1325, "y": 720},
    {"server_id": 28, "server_name": "OC-3", "region": "OC", "x": 1410, "y": 675},
    {"server_id": 29, "server_name": "OC-4", "region": "OC", "x": 1265, "y": 770},
    {"server_id": 30, "server_name": "OC-5", "region": "OC", "x": 1390, "y": 760},
)

MAP_ASSET_CANDIDATES: tuple[str, ...] = (
    "world_map.png",
    "assets/world_map.png",
    "assets/world_map.gif",
)

MIN_ZOOM = 0.6
MAX_ZOOM = 5.0
ZOOM_STEP = 1.12
LOD_LOW_MAX = 1.5
LOD_MEDIUM_MAX = 3.0
