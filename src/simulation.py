import pygame
from typing import List, Dict, Optional
from models import Drone, Zone, Connection
from parser import MapParser
from pathfinder import PathFinder
from visualizer import Visualizer


class Simulation:
    """Controller for running the drone simulation.

    Now supports interactive control from the Visualizer:
      - visualizer.attach_simulation(sim) is called by Simulation.run()
      - Visualizer will toggle sim.paused and set sim.current_turn
    """
    def __init__(self, parser: MapParser) -> None:
        self.zones: Dict[str, Zone] = parser.zones
        self.connections: List[Connection] = parser.connections
        self.start_hub: str = parser.start_hub or ""
        self.end_hub: str = parser.end_hub or ""
        self.nb_drones: int = parser.nb_drones
        self.drones: List[Drone] = []
        self._current_turn: int = 0
        self.turn_history: List[List[tuple[int, str, int, List[str]]]] = []
        self.turn_start_time: int = pygame.time.get_ticks()
        self.last_turn_updated: int = 0
        self.paused: bool = False

        self.pathfinder = PathFinder(
            self.zones, self.connections, self.start_hub,
            self.end_hub)
        self._initialize_drones()

    @property
    def current_turn(self) -> int:
        return self._current_turn

    @current_turn.setter
    def current_turn(self, value: int) -> None:
        if value < 0:
            value = 0
        if self.turn_history:
            max_index = len(self.turn_history) - 1
            if value > max_index:
                value = max_index
        self._current_turn = value
        self.turn_start_time = pygame.time.get_ticks()
        if self.turn_history:
            self._apply_turn_targets(self._current_turn)
            self.last_turn_updated = self._current_turn

    def _initialize_drones(self) -> None:
        for i in range(1, self.nb_drones + 1):
            drone = Drone(drone_id=i, current_zone=self.zones[self.start_hub])
            path = self.pathfinder.find_path_with_reservations(
                self.start_hub, self.end_hub, start_time=0
            )
            if path:
                simple_path = [step[0] for step in path]
                drone.set_path(simple_path)
                self._reserve_path_capacity(path)
            self.drones.append(drone)

    def _reserve_path_capacity(
            self, path: List[tuple[str, int]]) -> None:
        for i in range(len(path) - 1):
            previous_zone, t_start = path[i]
            current_zone, t_end = path[i+1]
            is_waiting = (current_zone == previous_zone)

            for time in range(t_start + 1, t_end + 1):
                self.pathfinder.add_reservation(current_zone, time)
                if not is_waiting:
                    self.pathfinder.add_link_reservation(previous_zone,
                                                         current_zone, time)

    def _snapshot_state(self) -> List[tuple[int, str, int, List[str]]]:
        """Create a lightweight snapshot of all drones for the current turn.

        Snapshot per drone: (drone_id, zone_name, wait_time, path_list)
        """
        return [
            (d.drone_id, d.current_zone.name, d.wait_time, list(d.path))
            for d in self.drones
        ]

    def _restore_state(self, snapshot:
                       List[tuple[int, str, int, List[str]]]) -> None:
        """Restore drones from a snapshot produced by _snapshot_state()."""
        id_to_drone = {d.drone_id: d for d in self.drones}
        for item in snapshot:
            did, zone_name, wait_time, path = item
            drone = id_to_drone.get(did)
            if drone:
                drone.current_zone = self.zones[zone_name]
                drone.wait_time = wait_time
                drone.path = list(path)

    def _reset_to_turn(self) -> None:
        """Alias used by visualizer: restore
        simulation to self.current_turn."""
        if 0 <= self._current_turn < len(self.turn_history):
            self._restore_state(self.turn_history[self._current_turn])

    def _apply_turn_targets(self, turn: int) -> None:
        """Apply stored state for `turn` (visualizer uses this)."""
        if 0 <= turn < len(self.turn_history):
            self._restore_state(self.turn_history[turn])

    def _advance_one_turn(self) -> Optional[List[str]]:
        """Advance simulation by one turn,
        executing moves and recording snapshot.

        Returns the printed move tokens for that turn (or None if no moves).
        """
        self._current_turn += 1
        moves_this_turn: List[str] = []

        for drone in self.drones:
            if not drone.has_arrived(self.end_hub):
                self._move_command(drone, moves_this_turn)

        self.turn_history = self.turn_history[:self._current_turn]
        self.turn_history.append(self._snapshot_state())
        self.turn_start_time = pygame.time.get_ticks()
        self.last_turn_updated = self._current_turn

        if moves_this_turn:
            print(f"{' '.join(moves_this_turn)}")
            return moves_this_turn
        return None

    def run(self, visualizer: Optional[Visualizer] = None) -> None:
        """Run the simulation until all drones reach the end hub.

        When a Visualizer is provided it:
          - receives attach_simulation(self)
          - handles pygame events (Visualizer must be the only consumer)
        """
        self._current_turn = 0
        self.turn_history = [self._snapshot_state()]
        self.turn_start_time = pygame.time.get_ticks()
        self.last_turn_updated = 0
        self.paused = False

        if visualizer:
            visualizer.attach_simulation(self)

        while not all(drone.has_arrived(self.end_hub)
                      for drone in self.drones):
            if visualizer:
                visualizer.draw_frame(
                    self.drones, self.connections,
                    self._current_turn, self.start_hub, self.end_hub)
                if self.paused:
                    pygame.time.delay(50)
                    continue
                self._advance_one_turn()
            else:
                self._advance_one_turn()
        return

    def _move_command(self, drone: Drone, move_this_turn: List[str]) -> None:
        if drone.wait_time > 0:
            drone.wait_time -= 1
            if drone.wait_time == 0:
                move_this_turn.append(f"D{drone.drone_id}-"
                                      f"{drone.current_zone.name}")
            return

        if not drone.path:
            return

        next_target_name = drone.path[0]

        if next_target_name == drone.current_zone.name:
            drone.path.pop(0)
            return

        next_zone = self.zones[next_target_name]

        if next_zone.zone_type == "restricted":
            conn_name = f"{drone.current_zone.name}-{next_target_name}"
            move_this_turn.append(f"D{drone.drone_id}-{conn_name}")
            drone.current_zone = next_zone
            drone.path.pop(0)
            drone.wait_time = 1
        else:
            drone.current_zone = next_zone
            drone.path.pop(0)
            move_this_turn.append(f"D{drone.drone_id}-{next_target_name}")
