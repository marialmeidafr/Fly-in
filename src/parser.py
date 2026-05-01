from typing import Optional, Dict, List
from models import Zone, Connection
import re


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
        self._validate_map() # fazer validate_map
    
    def _parse_line(self, line: str, line_num: int) -> None:
        # identifica se a linha é uma Zona ou uma Conexão.
        metadata_filter = re.search(r'\[(.*?)\]', line)
        metadata_str = metadata_filter.group(1) if metadata_filter else ""
        metadata_dict = self._parse_metadata(metadata_str) # fazer parse_metadata
        base_line = re.sub(r'\s*\[.*?\]\s*', '', line).strip()
        if (base_line.startswith("start_hub:")
            or base_line.startswith("end_hub:")
            or base_line.startswith("hub:")):
            self._parse_zone(base_line, metadata_dict, line_num) #fazer parse_zone
        elif base_line.startswith("connection:"):
            self._parse_connection(base_line, metadata_dict, line_num) # fazer parse_connection
        else:
            raise ValueError(f"Unknown syntax on line: {line_num}: {line}")
        
    def _parse_metadata(self, metadata_str: str) -> Dict[str, str]:
        # transforma uma str num dict
        if not metadata_str:
            return {}
        meta_dict: Dict[str, str] = {}
        for pair in metadata_str.split():
            if '=' in pair:
                key, value = pair.split('=', 1)
                meta_dict[key] = value
        return meta_dict
    

    def _parse_zone(self, base_line: str,
                    metadata: Dict[str, str], line_num: int) -> None:
        