import heapq
from typing import Dict, List, Set, Tuple, Optional
from models import Zone, Connection


class PathFinder:
    def __init__(self, zones: Dict[str, Zone],
                 connections: List[Connection], end_hub: str) -> None:
        self.zones = zones
        self.connections = connections
        self.graph: dict[str, List[str]] = self._build_graph()
        # evitar colisoes:
        self.reservations = Dict[Tuple[str, int], int] = {}
        self.link_capacities: Dict[Tuple[str, str], int] = {}
        self.link_reservations: Dict[Tuple[str, str, int], int] = {}
        self._init_link_capacities()
        # atalho baseado na distancia real de tempo
        self.strategic_map: Dict[str, int] = self._compute_true_distances(end_hub)
    
    def _build_graph(self) -> Dict[str, List[str]]:
        graph: Dict[str, List[str]] = {name: [] for name in self.zones}
        for connection in self.connection:
            graph[self.connection.zone_1.name].append(connection.zone_2.name)
            graph[self.connection.zone_2.name].append(connection.zone_1.name)
        return graph
    
    def _get_move_cost(self, zone_obj: Zone, is_waiting: bool = False) -> Optional[int]:
        if is_waiting:
            return 1
        if zone_obj.zone_type == "blocked":
            return None
        if zone_obj.zone_type == "restricted":
            return 2
        return 1
    
    def _compute_true_distances(self, end_hub: str) -> Dict[str, int]:
        distances: Dict[str, int] = {end_hub: 0}
        priority_zone: List[Tuple[int, str]] = [(0, end_hub)]
        while priority_zone:
            current_dist, current_node = heapq.heappop(priority_zone)
            if current_dist > distances.get(current_node, float('inf')):
                continue
            for neighbor in self.graph.get(current_node, []):
                # o custo se baseia em que zona ele entra
                target_zone = self.zones[current_node]
                move_cost = self._get_move_cost(target_zone)
                if move_cost is None:
                    continue

                new_dist = current_dist + move_cost
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    heapq.heappush(priority_zone, (new_dist, neighbor))
        return distances

    def _get_link_key(self, z1: str, z2: str) -> Tuple[str, str]:
        return (z1, z2) if z1 < z2 else (z2, z1)

    def _init_link_capacities(self) -> None:
        for connection in self.connections:
            key = self._get_link_key(connection.zone_1.name, connection.zone_2.name)
            self.link_capacities[key] = connection.max_link_capacity