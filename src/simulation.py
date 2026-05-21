import sys
import pygame
from typing import List, Dict, Optional

from models import Drone, Zone, Connection
from parser import MapParser
from pathfinder import PathFinder
from visualizer import Visualizer


class Simulation:
    def __init__(self, parser: MapParser) -> None:
        self.zones: Dict[str, Zone] = parser.zones
        self.connections: List[Connection] = parser.connections
        self.start_hub: str = parser.start_hub or ""
        self.end_hub: str = parser.end_hub or ""
        self.nb_drones: int = parser.nb_drones
        self.drones: List[Drone] = []
        self.turn: int = 0
        self.pathfinder = PathFinder(
            self.zones, self.connections, self.start_hub,
            self.end_hub)
        self._initialize_drones()

    def _initialize_drones(self) -> None:
        # cria os drones e planeia as rotas sem colisoes
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

    def _reserve_path_capacity(
            self, path: List[tuple[str, int]]) -> None:
        # marca no meu algoritmo as zonas e as conexoes que o drone vai usar
        for i in range(len(path) - 1):
            previous_zone, t_start = path[i]
            current_zone, t_end = path[i+1]
            is_waiting = (current_zone == previous_zone)

            for time in range(t_start + 1, t_end + 1):
                self.pathfinder.add_reservation(current_zone, time)
                if not is_waiting:
                    self.pathfinder.add_link_reservation(previous_zone, current_zone, time)

    def run(self, visualizer: Optional[Visualizer] = None) -> None:
        # executa a simulacao turno a turno
        print("--- Flying ---")
        while not all(drone.has_arrived(self.end_hub) for drone in self.drones):
            self.turn += 1
            moves_this_turn: List[str] = []

            for drone in self.drones:
                if not drone.has_arrived(self.end_hub):
                    self._move_command(drone, moves_this_turn)

            if moves_this_turn:
                print(f"Turn {self.turn}: {' '.join(moves_this_turn)}")

            if visualizer:
                # Lidar com fecho da janela
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Desenha o estado atual
                visualizer.draw_frame(
                    self.drones, self.connections,
                    self.turn, self.start_hub, self.end_hub)

        # Log no terminal (obrigatório)
        if moves_this_turn:
            print(f"Turn {self.turn}: {' '.join(moves_this_turn)}")
        print(f"--- Finish (Total: {self.turn} turns) ---")

    def _move_command(self, drone: Drone, move_this_turn: List[str]) -> None:
        # gestão de Trânsito (Zonas Restritas/Custo 2)
        if drone.wait_time > 0:
            drone.wait_time -= 1
            if drone.wait_time == 0:
                move_this_turn.append(f"D{drone.drone_id}-{drone.current_zone.name}")
            return

        if not drone.path:
            return

        # iniciar um novo momvimento
        next_target_name = drone.path[0]

        # se eu estiver que esperar na mesma zona
        if next_target_name == drone.current_zone.name:
            drone.path.pop(0)
            return

        next_zone = self.zones[next_target_name]

        if next_zone.zone_type == "restricted":
            # imprime a entrada na ligacao
            conn_name = f"{drone.current_zone.name}-{next_target_name}"
            move_this_turn.append(f"D{drone.drone_id}-{conn_name}")

            # atualiza o estado, mas em transito
            drone.current_zone = next_zone
            drone.path.pop(0)
            drone.wait_time = 1
        else:
            # movimento normal
            drone.current_zone = next_zone
            drone.path.pop(0)
            move_this_turn.append(f"D{drone.drone_id}-{next_target_name}")
