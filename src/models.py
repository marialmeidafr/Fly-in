from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class Zone:
    """Representation of a map zone/node.

    Attributes:
        name: Unique zone identifier.
        x: X coordinate on the map.
        y: Y coordinate on the map.
        max_drones: Maximum number of drones that can occupy the zone.
        zone_type: Type of the zone (e.g. 'normal', 'priority').
        color: Optional color string used by visualizer.
        drones_presents: List of drone ids currently present.
    """
    name: str
    x: int
    y: int
    max_drones: int = 1
    zone_type: str = "normal"
    color: Optional[str] = None
    drones_presents: List[int] = field(default_factory=list)
    # avoids all class objects sharing the same list

    def __post_init__(self) -> None:
        """Validate zone type and capacity after initialization.

        Raises:
            ValueError: If `zone_type` is invalid or `max_drones` < 1.
        """
        valid_types = {"normal", "blocked", "restricted", "priority"}
        if self.zone_type not in valid_types:
            raise ValueError(
                f"Zone {self.zone_type} not recognized"
            )
        if self.max_drones < 1:
            raise ValueError(
                f"max_drones must be positive in zone {self.name}"
            )

    @property
    def is_full(self) -> bool:
        """Return True if the zone is at or above capacity.

        Returns:
            bool: True when number of present drones >= max_drones.
        """
        return len(self.drones_presents) >= self.max_drones


@dataclass
class Connection:
    """Represents a bidirectional connection between two `Zone`s.

    Attributes:
        zone_1: First endpoint zone.
        zone_2: Second endpoint zone.
        max_link_capacity: Max number of drones that can traverse
        the link simultaneously.
        traffic_drones: Current number of drones using the link.
    """
    zone_1: Zone
    zone_2: Zone
    max_link_capacity: int = 1
    traffic_drones: int = 0

    def __post_init__(self) -> None:
        """Validate link capacity after initialization.

        Raises:
            ValueError: If `max_link_capacity` is less than 1.
        """
        if self.max_link_capacity < 1:
            raise ValueError(
                "max_link_capacity must be at least 1"
            )

    @property
    def can_traverse(self) -> bool:
        """Return True if at least one additional drone can
        traverse the link."""
        return self.traffic_drones < self.max_link_capacity

    def reset_traffic(self) -> None:
        """Reset the current traffic counter for the connection to zero."""
        self.traffic_drones = 0

    def name(self) -> str:
        """Return a human-readable name for the connection.

        Returns:
            str: Concatenation of both zone names with a hyphen.
        """
        return f"{self.zone_1.name}-{self.zone_2.name}"


@dataclass
class Drone:
    """Model of a drone in the simulation.

    Attributes:
        drone_id: Unique integer identifier.
        current_zone: Zone where the drone currently is.
        path: Ordered list of zone names the drone will follow.
        status: Current status string (e.g. 'moving').
        wait_time: Turns left to wait (for restricted zones).
    """
    drone_id: int
    current_zone: Zone
    path: List[str] = field(default_factory=list)
    status: str = "moving"
    wait_time: int = 0

    def has_arrived(self, end_zone: str) -> bool:
        """Return True when drone has reached the `end_zone`.

        Args:
            end_zone: Name of the target end zone.

        Returns:
            bool: True if current zone name equals `end_zone`.
        """
        return self.current_zone.name == end_zone

    def set_path(self, new_path: List[str]) -> None:
        """Assign a new path to the drone and normalize the first step.

        If the first element of `new_path` matches the drone's current zone,
        it is removed so the drone does not attempt to move to its
        present location.

        Args:
            new_path: List of zone names representing the planned route.
        """
        self.path = new_path
        if self.path and self.path[0] == self.current_zone.name:
            self.path.pop(0)


@dataclass
class World:
    """Container for the simulation world state.

    Attributes:
        nb_drones: Number of drones in the world.
        zones: Mapping of zone name to `Zone` objects.
        connections: List of `Connection` objects describing links.
        drones: List of `Drone` instances present in the world.
    """
    nb_drones: int
    zones: Dict[str, Zone]
    connections: List[Connection]
    drones: List[Drone] = field(default_factory=list)
