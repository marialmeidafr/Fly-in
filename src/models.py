from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Zone:
    name: str
    x: int
    y: int
    max_drones: int = 1
    type: str = "normal"
    color: Optional[str] = None

@dataclass
class Connection:
    zone_a: str
    zone_b: str
    max_capacity: int = 1
    cost: float = 1.0