
<div align="center">
  <h1 align="center">Fly-in 🚁 </h1>
</div>

<p align="center">
  <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWgwcWl4dXpqejhudmV4bnMzZGcwemNiMXVmMjNlbXMzc3N3Z29uNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jCXruLiF9zoofTkmpo/giphy.gif" width="300" alt="fun gif"/>
</p>

*This project has been created as part of the 42 curriculum by mariaalm.*

## Description
Fly-in is a route-planning and simulation project where a fleet of drones must travel from a start hub to an end hub through a network of zones and connections.

The goal is to compute safe, conflict-aware paths while respecting zone capacity, link capacity, and the special movement rules of restricted zones. The program can run in text mode or in a visual mode powered by Pygame.

The project parses a custom map format, builds the travel graph, plans drone paths with reservations, and simulates the trip turn by turn until every drone reaches the destination.

## Instructions

### Requirements
- Python 3.10
- Pygame

### Installation
The repository includes a Makefile that creates a virtual environment and installs the required tools.

```bash
make install
```

This installs:
- `pygame`
- `flake8`
- `mypy`

### Execution
First install the local environment:

```bash
make install
```

Run the simulation in text mode:

```bash
make run ARGS=maps/easy/01_linear_path.txt
```

Run the simulation with the visual interface:

```bash
make visual ARGS=maps/easy/01_linear_path.txt
```

You can also run the entry point directly:

```bash
./venv/bin/python src/main.py maps/easy/01_linear_path.txt
./venv/bin/python src/main.py maps/easy/01_linear_path.txt --visual
```

### Useful commands
```bash
make lint
make lint-strict
make clean
make fclean
```

## Algorithm Choices and Implementation Strategy

### 1. Map parsing and validation
The parser reads a custom text map format and extracts:
- the number of drones
- the start hub
- the end hub
- all zones
- all connections

Validation ensures that:
- zone names are unique
- coordinates are integers
- only one start hub and one end hub exist
- connections reference known zones
- a valid path exists between start and end
- zone types and capacities are valid

### 2. Graph representation
The map is stored as an adjacency list so the travel network can be traversed efficiently.
Connections are also stored with their capacity, which allows the simulation to respect link congestion rules.

### 3. Time-aware pathfinding
The core pathfinding logic is implemented with a priority queue and a time-based search strategy.
The algorithm does not only care about distance, but also about:
- zone cost
- waiting time
- reserved zones
- reserved connections
- zone capacity
- link capacity

Restricted zones cost more to enter, and blocked zones are excluded.
Priority zones are favored with a small bonus in the heuristic.

The implementation keeps reservation tables for:
- zone occupancy per time step
- connection usage per time step

This prevents drones from being assigned conflicting routes.

### 4. Drone planning strategy
Each drone is planned sequentially.
After a path is found for one drone, its route is reserved in the global tables so the next drones are planned around the already occupied zones and connections.
This greedy reservation-based approach is simple, deterministic, and works well for the turn-based simulation used in the project.

### 5. Turn-based simulation
The simulation advances one turn at a time.
For each turn, every drone either:
- moves to the next zone
- waits if the path requires it
- spends extra time when entering a restricted zone

The simulation stops when all drones arrive at the end hub.

## Visual Representation
The visual mode is designed to make the simulation easy to understand at a glance.

### Main visual features
- pastel background and soft colors
- start and end hubs shown with larger icons
- drones drawn directly on the zone they currently occupy
- drone labels hidden on the start and end hubs for a cleaner look
- gray connections to keep the map readable without competing with zone colors
- turn counter displayed at the top for quick progress tracking

### User experience improvements
The visual interface helps by:
- making the route structure easy to follow
- showing drone movement turn by turn
- distinguishing special zones through color and capacity rules
- keeping the start and end hubs visually prominent
- reducing clutter with simplified connection colors and label placement

The current layout is tuned for readability rather than realism, which makes it easier to follow the simulation during tests and demonstrations.

## Resources

### References
- Python documentation: https://docs.python.org/3/
- `heapq` module: https://docs.python.org/3/library/heapq.html
- `dataclasses` module: https://docs.python.org/3/library/dataclasses.html
- Pygame documentation: https://www.pygame.org/docs/
- A* search algorithm overview: https://en.wikipedia.org/wiki/A*_search_algorithm
- Graph representation and traversal basics: https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/

### AI usage
AI was used to:
- draft and structure this README in English
- help summarize the implementation strategy from the existing source code
- document the visual choices in a clear project-friendly format

AI was not used to generate the project logic itself; the code and behavior described here come from the repository implementation.
