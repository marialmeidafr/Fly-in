from dataclasses import dataclass, field
from typing import Optional, Dict, List
from models import Zone, Connection


class MapParser:
    def __init__(self,  file_path: str):
        self.file_path = file_path
        self.drone_count: int = 0
        self.start_hub: Optional[str] = None
        self.end_hub: Optional[str] = None
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
    
    def parse(self) -> None:
        try:
            with open(self.file_path, 'r', enconding='utf-8') as f:
                content = f.read()
            lines = content.splitlines()
            for line in lines:
                clean = line.split('#')[0].strip()
                if clean.startswith("drone_count:"):
                    
        except Exception as error:
            print(f"Error to open the map: {error}")
            exit(1)