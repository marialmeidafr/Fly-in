from typing import Optional, Dict, List, Set, Tuple
from models import Zone, Connection
import re


class MapParser:
    def __init__(self,  file_path: str) -> None:
        """Initialize the parser with a map file path and empty state."""
        self.file_path = file_path
        self.nb_drones: int = 0
        self.start_hub: Optional[str] = None
        self.end_hub: Optional[str] = None
        self.zones: Dict[str, Zone] = {}
        self.duplicated_connections: Set[Tuple[str, str]] = set()
        self.connections: List[Connection] = []
    
    def parse(self) -> None:
        """Load, parse, and validate the map file contents."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            lines = content.splitlines()
            # encontrar quantidade de drones
            for line in lines:
                clean = line.split('#')[0].strip()
                if clean.startswith("nb_drones:"):
                    try:
                        self.nb_drones = int(clean.split(':')[1].strip())
                        break
                    except ValueError:
                        raise ValueError("Invalid nb_drones format.")
            if self.nb_drones <= 0:
                raise ValueError("nb_drones missing or invalid")
            # processa zonas e conexoes
            for line_num, line in enumerate(lines, 1):
                clean = line.split('#')[0].strip()
                if not clean or clean.startswith("nb_drones:"):
                    continue
                self._parse_line(clean, line_num)
            self._validate_map()
        except Exception as error:
            print(f"Error to open the map: {error}")
            exit(1)
    
    def _parse_line(self, line: str, line_num: int) -> None:
        """Parse one line of input as either a zone or a connection."""
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
        """Convert a metadata string into a dictionary."""
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
        """Parse a zone declaration and store it in the parser state."""
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
        if final_max < 1:
            raise ValueError(f"Error in line {line_num}: max_drones must be a positive integer")
        else:
            if prefix_zone in ('start_hub:', 'end_hub:'):
                final_max = self.nb_drones
            else:
                final_max = 1
        zona_type = metadata.get('zone', 'normal')
        # tipo da zona
        valid_types = ('normal', 'blocked', 'restricted', 'priority')
        if zona_type not in valid_types:
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
        """Parse a connection declaration and add it to the parser state."""
        parts = base_line.split()
        if len(parts) != 2:
            raise ValueError(f"Error in line: {line_num}: invalid format")
        try:
            connectors: str = parts[1]
            zone_1, zone_2 = connectors.split('-')
        except ValueError:
            raise ValueError(f"Error on line {line_num}: invalid  connection format")
        if zone_1 not in self.zones or zone_2 not in self.zones:
            raise ValueError(f"Error on line {line_num}: connection to unknown zone ({zone_1}or {zone_2})")
        if zone_1 <= zone_2: # garantir que A==B e B==A
            pair: Tuple[str, str] = (zone_1, zone_2)
        else:
            pair = (zone_2, zone_1)
        if pair in self.duplicated_connections:
            raise ValueError(f"Error on line {line_num}: duplicate connection {zone_1}-{zone_2}")
        self.duplicated_connections.add(pair)
        z1 = self.zones[zone_1]
        z2 = self.zones[zone_2]
        connection = Connection(
            zone_1=z1,
            zone_2=z2,
            max_link_capacity=int(metadata.get('max_link_capacity', 1))
        )
        self.connections.append(connection)
    
    
    def _get_neighbor(self, connection: Connection, current_zone_name: str) -> Optional[str]:
        """Return the adjacent zone name for a bidirectional connection."""
        zone_1_name: str = connection.zone_1.name
        zone_2_name: str = connection.zone_2.name
        if zone_1_name == current_zone_name:
            return zone_2_name
        if zone_2_name == current_zone_name:
            return zone_1_name
        return None
    
    def _has_path(self, start: str, end: str) -> bool:
        """Check whether there is a non-blocked path between two zones."""
        zones_visited = {start}
        next_zones = [start]

        while next_zones:
            path = next_zones.pop(0)
        
            if path == end:
                return True
            
            for connection in self.connections:
                neighbor = self._get_neighbor(connection, path)

                if neighbor and neighbor not in zones_visited:
                    if self.zones[neighbor].zone_type != "blocked":
                        zones_visited.add(neighbor)
                        next_zones.append(neighbor)
        return False

    def _validate_map(self) -> None:
        """Validate the parsed map and required endpoints."""
        if self.nb_drones <= 0:
            raise ValueError(f"The number of drones must be a positive number")
        if not self.start_hub:
            raise ValueError(f"There must be a starting zone")
        if not self.end_hub:
            raise ValueError(f"There must be an end zone")
        if not self._has_path(self.start_hub, self.end_hub):
            raise ValueError(f"There must be a path")
