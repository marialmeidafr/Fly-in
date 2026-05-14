import heapq
from models import Zone, Connection


class PathFinder:
    def __init__(self, zones: dict[str, Zone],
                 connections: list[Connection], end_hub: str) -> None:
        