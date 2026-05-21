import heapq
from typing import Dict, List, Set, Tuple, Optional
from models import Zone, Connection


class PathFinder:
    def __init__(
            self, zones: Dict[str, Zone],
            connections: List[Connection], start_hub: str,
            end_hub: str) -> None:
        self.zones = zones
        self.connections = connections
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.map: dict[str, List[str]] = self._build_map()
        # evita colisoes
        self.reservations: Dict[Tuple[str, int], int] = {}
        self.link_capacities: Dict[Tuple[str, str], int] = {}
        self.link_reservations: Dict[Tuple[str, str, int], int] = {}
        self._init_link_capacities()
        # shortcuts based on true time distance
        self.strategic_map: Dict[str, int] = (
            self._calculate_the_strategic_map(end_hub))

    def _build_map(self) -> Dict[str, List[str]]:
        graph: Dict[str, List[str]] = {
            name: [] for name in self.zones}
        for connection in self.connections:
            graph[connection.zone_1.name].append(
                connection.zone_2.name)
            graph[connection.zone_2.name].append(
                connection.zone_1.name)
        return graph

    def _get_move_cost(self, zone_obj: Zone, is_waiting: bool = False) -> Optional[int]:
        if is_waiting:
            return 1
        if zone_obj.zone_type == "blocked":
            return None
        if zone_obj.zone_type == "restricted":
            return 2
        return 1

    def _calculate_the_strategic_map(
            self, end_hub: str) -> Dict[str, int]:
        distances: Dict[str, int] = {end_hub: 0}
        priority_zone: List[Tuple[int, str]] = [(0, end_hub)]
        while priority_zone:
            current_dist, current_node = heapq.heappop(priority_zone)
            if current_dist > distances.get(current_node, float('inf')):
                continue
            for neighbor in self.map.get(current_node, []):
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

    def add_reservation(self, zone_name: str, time: int) -> None:
        if zone_name in (self.start_hub, self.end_hub):
            return
        key = (zone_name, time)
        self.reservations[key] = self.reservations.get(key, 0) + 1

    def add_link_reservation(self, z1: str, z2: str, time: int) -> None:
        key = self._get_link_key(z1, z2)
        full_key = (key[0], key[1], time)
        self.link_reservations[full_key] = self.link_reservations.get(full_key, 0) + 1

    def find_path_with_reservations(
            self, start: str, end: str,
            start_time: int) -> List[Tuple[str, int]]:
        open_set: List[Tuple[float, int, str, List[Tuple[str, int]]]] = []

        initial_h = self.strategic_map.get(start, 999)
        heapq.heappush(
            open_set,
            (start_time + initial_h, start_time, start,
             [(start, start_time)]))

        visited: Set[Tuple[str, int]] = {(start, start_time)}

        while open_set:
            _, current_time, curr_name, path = heapq.heappop(
                open_set)

            if curr_name == end:
                return path

            # movimentos possíveis: vizinhos + ficar parado(esperando)
            possible_moves = self.map.get(curr_name, []) + [curr_name]

            for next_name in possible_moves:
                is_waiting = (next_name == curr_name)
                next_zone = self.zones[next_name]
                move_cost = self._get_move_cost(
                    next_zone, is_waiting)
                if move_cost is None:
                    continue
                arrival_time = current_time + move_cost

                # verificação de Conflitos (Capacidade de Zona e Link)
                conflict = False
                link_key = (
                    self._get_link_key(curr_name, next_name)
                    if not is_waiting else None)

                for time in range(current_time + 1, arrival_time + 1):
                    # capacidade da Zona (exceto Start/End)
                    if next_name not in (self.start_hub, self.end_hub):
                        reserved = self.reservations.get(
                            (next_name, time), 0)
                        if reserved >= next_zone.max_drones:
                            conflict = True
                            break

                    # capacidade da Ligação (Link)
                    if link_key:
                        max_cap = self.link_capacities.get(
                            link_key, 1)
                        reserved_link = self.link_reservations.get(
                            (link_key[0], link_key[1], time), 0)
                        if reserved_link >= max_cap:
                            conflict = True
                            break

                if conflict:
                    continue

                state = (next_name, arrival_time)
                if state not in visited:
                    visited.add(state)
                    # Cost calculation for bonus (45 turns)
                    h_cost = self.strategic_map.get(
                        next_name, 999)
                    priority_bonus = (
                        0.5 if next_zone.zone_type == "priority"
                        else 0.0)
                    # Traffic penalty for alternative paths
                    congestion_factor = (
                        self.reservations.get(
                            (next_name, arrival_time), 0) * 0.2)

                    # f(n) = g(n) + h(n) - bonus + penalty
                    estimated_cost = (
                        arrival_time + h_cost - priority_bonus +
                        congestion_factor)
                    new_path = path + [(next_name, arrival_time)]
                    heapq.heappush(
                        open_set,
                        (estimated_cost, arrival_time,
                         next_name, new_path))

        return []
