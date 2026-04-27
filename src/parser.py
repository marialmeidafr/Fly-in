from dataclasses import dataclass, field
from typing import Optional, Dict, List
from models import Zone, Connection


@dataclass
class Zone:
    name: str
    x: int
    y: int
    max_drones: int = 1
    type: str = "normal"
    color: str = "white"

@dataclass
class Link:
    zone_a: str
    zone_b: str
    max_capacity: int = 1
    cost: float = 1.0

class MapParser:
    def __init__(self,  file_path: str):
        self.file_path = file_path
        self.drone_count: 