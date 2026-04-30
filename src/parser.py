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
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            lines = content.splitlines()
            # encontrar quantidade de drones
            for line in lines:
                clean = line.split('#')[0].strip()
                if clean.startswith("drone_count:"):
                    try:
                        self.drone_count = int(clean.split(':')[1].strip())
                        break
                    except ValueError:
                        raise ValueError("Invalid drone_count format.")
            if self.drone_count <= 0:
                raise ValueError("Drone_count missing or invalid")
            # processa zonas e conexoes
            for line_num, line in enumerate(lines, 1):
                clean = line.split('#')[0].strip()
                if not clean or clean.startswith("drone_count:"):
                    continue
        except Exception as error:
            print(f"Error to open the map: {error}")
            exit(1)
    
    def _parse_line(self, line: str, line_num: int) -> None:
        # identifica se a linha é uma Zona ou uma Conexão.

        