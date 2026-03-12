# Game Server Infrastructure Simulation System — Iteration 1

This project implements Iteration 1 of the simulation using Python standard library only.

## Scope included
- Simulation start/stop lifecycle
- Preset servers toggled ON/OFF by region
- Automatic player generation
- Player assignment to nearest server
- Room creation only when 5 free players are waiting on one server
- Room expiration at 60 seconds
- Free-player timeout reassignment after 5 seconds
- Server load calculation
- Regional CQI + Global CQI calculation
- Interactive real-time tkinter visualization (pan/zoom, LOD details)

## Scope excluded
- Economics and finance
- Server upgrades/selling
- Tier/profit/report logic
- Persistence

## Run
```bash
python -m src.game_server_sim.main
```

## Optional real map background
Place an image file at one of these paths:
- `assets/world_map.png`
- `assets/world_map.gif`

If missing, the app still runs with a fallback background and region boundaries.

## UI controls
- Start / Stop simulation
- Left click server: select target server
- Toggle Selected Server: switch ON/OFF for selected server
- RMB drag: pan map
- Mouse wheel: zoom map
- Left click player/server: inspect nearest entity

## Test
```bash
python -m unittest discover -s tests -v
```
