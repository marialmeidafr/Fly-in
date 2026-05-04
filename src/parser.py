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
        parts: list[str] = base_line.split()
        if len(parts) != 4:
            raise ValueError(f"Error in line: {line_num}: invalid format")
        prefix_zone = parts[0]
        name_zone = parts[1]
        if '-' in name_zone:
            raise ValueError(f"Error in line: {line_num}: forbids dashes in zone names")
        if name_zone in self.zones:
            raise ValueError(f"Error in line: {line_num}: zone name {name_zone} already exists")
        try:
            x = int(parts[2])
            y = int(parts[3])
        except ValueError:
            raise ValueError(f"Error in line: {line_num}: coordinates must be an int")
        max_drones = metadata.get('max_drones')
        # qnts drones cabem por turno
        if max_drones is not None:
            final_max = int(max_drones)
        else:
            if prefix_zone in ('start_hub:', 'end_hub:'):
                final_max = self.drone_count
            else:
                final_max = 1
        zona_type = metadata.get('zone', 'normal')
        # tipo da zona
        if zona_type is not ('normal', 'blocked', 'restricted', 'priority'):
            raise ValueError(f"Error in line {line_num}: invalid zone {zona_type}")
        zone = Zone(name=name_zone, x=x, y=y, zona_type=zona_type,
                    color=metadata.get('color', 'white'), max_drones=final_max)
        self.zones[name_zone] = zone
        if prefix_zone == "start_hub:":
        # defino uma unica entrada e uma unica saida
            if self.start_hub:
                raise ValueError(f"Error in line: {line_num}: There can only be one start_hub")
            self.start_hub = name_zone
        elif prefix_zone == "end_hub:":
            if self.end_hub:
                raise ValueError(f"Error in line: {line_num}: There can only be one end_hub")
            self.end_hub = name_zone
    
    def _parse_connection(self, base_line: str,
                    metadata: Dict[str, str], line_num: int) -> None:
        
        
        