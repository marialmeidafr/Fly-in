from dataclasses import dataclass, field
from typing import Optional
import math

@dataclass
class Zone:
    name: str
    x: int
    y: int
    max_drones: int = 1
    zone_type: str = "normal"
    color: Optional[str] = "white"

@dataclass
class Connection:
    zone_1: Zone
    zone_2: Zone
    max_link_capacity: int = 1
    
    @property
    def distance(self) -> float:
        return math.sqrt(
            (self.zone_1.x - self.zone_2.x)**2 + 
            (self.zone_1.y - self.zone_2.y)**2
        )