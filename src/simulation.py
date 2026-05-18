from typing import List, Dict, Optional
from models import Drone, Zone, Connection
from parser import MapParser
from pathfinder import PathFinder
from visualizer import Visualizer


class Sminulation:
    def __init__(self, parser: MapParser) -> None:
        self.zones: Dict[str, Zone] = parser.zones
        self.connections: List[Connection] = parser.connections
        self.start_hub: str = parser.start_hub or ""
        self.end_hub: str = parser.end_hub or ""
        self.nb_drones: int = parser.nb_drones
        self.drones: List[Drone] = []
        self.turn: int = 0
        self.pathfinder = PathFinder(self.zones, self.connections, self.end_hub)
        self.initialize_drones()
    
    def _initialize_drones(self) -> None:
        for i in range(1, self.nb_drones + 1):
            drone = Drone(drone_id=i, current_zone=self.zones[self.start_hub])
            # planeia o caminho considerando reservas de drones anteriores
            path = self.pathfinder.find_path_with_reservations(
                self.start_hub, self.end_hub, start_time=0
            )
            if path:
                simple_path = [step[0] for step in path]
                drone.set_path(simple_path)
                self._reserve_path_capacity(path)
            self.drones.append(drone)

    def _reserve_path_capacity(self, path: List[tuple[str, int]]) -> None:
        for i in range(len(path) - 1):
            prev_zone, t_start = path[i]
            curr_zone, t_end = path[i+1]
            is_waiting = (curr_zone == prev_zone)

            for t in range(t_start + 1, t_end + 1):
                self.pathfinder.add_reservation(curr_zone, t)
                if not is_waiting:
                    self.pathfinder.add_link_reservation(prev_zone, curr_zone, t)
    
    def run(self) -> None:
        print("--- Flying ---")