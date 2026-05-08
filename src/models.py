from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass # ajuda a criar classes, nao preciso fazer o init, ele ja faz automatico
class Zone:
    # Deve armazenar o tipo (normal, priority, etc.), 
    # as coordenadas e, crucialmente, a sua capacidade atual (max_drones)
    name: str
    x: int
    y: int
    max_drones: int = 1
    zone_type: str = "normal"
    color: Optional[str] = None
    drones_presents: List[int] = field(default_factory=list) # evta que todos os obejtos da classe
                                                            # compartilhem a mesma lista
    def __post_init__(self) -> None:
        valid_types = {"normal", "blocked", "restricted", "priority"}
        if self.zone_type not in valid_types:
            raise ValueError(f"")
        if self.max_drones < 1:
            raise ValueError(f"")

    @property
    def is_full(self) -> bool:
        return len(self.drones_presents) >= self.max_drones

@dataclass
class Connection:
    # Deve gerir a ligação entre duas zonas e a sua max_link_capacity
    zone_1: Zone
    zone_2: Zone
    max_link_capacity: int = 1
    traffic_drones: int = 0

    def __post_init__(self) -> None:
        if self.max_link_capacity < 1:
            raise ValueError(f"")

@dataclass
class Drone:
    # Cada drone deve ter um identificador único e saber o seu estado (se está numa zona, 
    # numa ligação para uma zona restrita ou se já chegou ao destino)
    drone_id: int
    current_zone: Zone
    path: List[str] = field(default_factory=list)
    status: str = "ready"
    wait_time: int = 0

    def has_arrived(self, end_zone: str) -> bool:
        return self.current_zone.name == end_zone
    
    def set_path(self, new_path: List[str]) -> None:
        self.path = new_path
        if self.path and self.path[0] == self.current_zone.name:
            self.path.pop(0)

@dataclass
class World:
    #  Uma classe que contenha todas as zonas e conexões,
    # servindo de base para o algoritmo de procura de caminho
    drone_count: int
    zones: Dict[str, Zone]
    connections: List[Connection]
    drones: List[Drone] = field(default_factory=list)
