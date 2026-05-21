import pygame
import sys
from models import Zone, Drone, Connection
from typing import List, Dict

class Visualizer:
    def __init__(self, zones: Dict[str, Zone], width: int = 1200, height: int = 800):
        pygame.init()
        pygame.display.set_caption("Fly-in")
        # Cores Profissionais
        self.CLR_BG = (10, 10, 15)
        self.CLR_LINE = (40, 45, 60)        
        self.CLR_CONN_GRAY = (140, 140, 140)
        self.CLR_TILE_PRIO = (135, 206, 250)  
        self.CLR_TILE_RESTR = (150, 50, 50) 
        self.CLR_TILE_NORMAL = (60, 179, 113)
        self.CLR_HUB = (255, 215, 0) # AMRELO IGUAL
        
        self.screen = pygame.display.set_mode((width, height))
        
        try:
            # Garante que a imagem está em assets/drone.png
            self.drone_img = pygame.image.load("assets/drone2.png").convert_alpha()
            self.drone_img = pygame.transform.scale(self.drone_img, (50, 50))
        except:
            self.drone_img = None
            
        self.font_id = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_hub = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_turn = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_legend = pygame.font.SysFont("Arial", 13, bold=True)
        
        self.zones = zones
        self._calculate_scaling()
        
        # No smoothing: drones appear instantly at their zone centers
        # Cores para traçar o caminho planeado de cada drone
        self.drone_colors = [
            (255, 99, 71),   # Tomato
            (30, 144, 255),  # DodgerBlue
            (60, 179, 113),  # MediumSeaGreen
            (238, 130, 238), # Violet
            (255, 215, 0),   # Gold
            (255, 105, 180), # HotPink
        ]
        self.clock = pygame.time.Clock()

    def _calculate_scaling(self):
        all_x = [z.x for z in self.zones.values()]
        all_y = [z.y for z in self.zones.values()]
        self.min_x, self.max_x = min(all_x), max(all_x)
        self.min_y, self.max_y = min(all_y), max(all_y)
        self.pad = 120 

    def _scale(self, x: int, y: int) -> tuple[int, int]:
        w, h = self.screen.get_size()
        rx = (self.max_x - self.min_x) or 1
        ry = (self.max_y - self.min_y) or 1
        nx = self.pad + (x - self.min_x) * (w - 2 * self.pad) // rx
        ny = self.pad + (y - self.min_y) * (h - 2 * self.pad) // ry
        return (int(nx), int(ny))

    def _draw_legend(self) -> None:
        width = 235
        height = 160
        margin = 18
        x = self.screen.get_width() - width - margin
        y = self.screen.get_height() - height - margin
        box = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (18, 18, 24), box, 0, 8)
        pygame.draw.rect(self.screen, (90, 90, 105), box, 1, 8)

        title = self.font_legend.render("LEGEND", True, (255, 255, 255))
        self.screen.blit(title, (x + 14, y + 12))

        entries = [
            (self.CLR_HUB, "START / END"),
            (self.CLR_TILE_PRIO, "PRIORITY"),
            (self.CLR_TILE_NORMAL, "NORMAL"),
            (self.CLR_TILE_RESTR, "RESTRICTED"),
        ]

        line_y = y + 40
        for color, label in entries:
            swatch = pygame.Rect(x + 14, line_y + 2, 16, 16)
            pygame.draw.rect(self.screen, color, swatch, 0, 3)
            text = self.font_legend.render(label, True, (255, 255, 255))
            self.screen.blit(text, (x + 40, line_y))
            line_y += 24

        pygame.draw.line(self.screen, self.CLR_CONN_GRAY, (x + 14, line_y + 10), (x + 42, line_y + 10), 3)
        conn_text = self.font_legend.render("CONNECTION", True, (255, 255, 255))
        self.screen.blit(conn_text, (x + 50, line_y + 2))

    def draw_frame(self, drones: List[Drone], connections: List[Connection], turn: int, start_node: str, end_node: str):
        self.screen.fill(self.CLR_BG)

        turn_label = self.font_turn.render(f"TURN {turn}", True, (255, 255, 255))
        self.screen.blit(turn_label, (20, 18))

        # 1. DESENHAR LINHAS (O Caminho)
        # Primeiro, calcule quais arestas são usadas pelos caminhos planeados
        used_edges = set()
        for drone in drones:
            planned = [drone.current_zone.name] + list(drone.path)
            for i in range(len(planned) - 1):
                a = planned[i]
                b = planned[i + 1]
                key = tuple(sorted((a, b)))
                used_edges.add(key)

        # Desenhar todas as conexões: se NÃO usadas -> linha branca mais grossa;
        # se usadas -> linha discreta (CL TONE) e o caminho planeado será desenhado por cima.
        for conn in connections:
            z1_name = conn.zone_1.name
            z2_name = conn.zone_2.name
            # Skip connections if neither endpoint has a visible "tile" (start/end/priority/restricted)
            z1 = self.zones.get(z1_name)
            z2 = self.zones.get(z2_name)
            if not z1 or not z2:
                continue
            visible_types = {"restricted", "priority", "normal"}
            z1_has_tile = (z1.zone_type in visible_types) or (z1_name == start_node) or (z1_name == end_node)
            z2_has_tile = (z2.zone_type in visible_types) or (z2_name == start_node) or (z2_name == end_node)
            if not (z1_has_tile or z2_has_tile):
                # neither endpoint has a drawn square -> skip this connection
                continue

            key = tuple(sorted((z1_name, z2_name)))
            p1 = self._scale(z1.x, z1.y)
            p2 = self._scale(z2.x, z2.y)
            if key in used_edges:
                # used connection: draw subtle thin gray line (will be emphasized by planned path)
                pygame.draw.line(self.screen, self.CLR_CONN_GRAY, p1, p2, 2)
            else:
                # unused connection: draw thicker gray line for subtle background
                pygame.draw.line(self.screen, self.CLR_CONN_GRAY, p1, p2, 5)

        # Desenhar o caminho planeado por cada drone (linha colorida, por cima)
        for drone in drones:
            planned = [drone.current_zone.name] + list(drone.path)
            if len(planned) < 2:
                continue
            color = self.drone_colors[(drone.drone_id - 1) % len(self.drone_colors)]
            for i in range(len(planned) - 1):
                a = self.zones.get(planned[i])
                b = self.zones.get(planned[i + 1])
                if not a or not b:
                    continue
                pa = self._scale(a.x, a.y)
                pb = self._scale(b.x, b.y)
                pygame.draw.line(self.screen, color, pa, pb, 4)

        # 2. ZONAS (Apenas START, END e Especiais)
        for name, zone in self.zones.items():
            pos = self._scale(zone.x, zone.y)
            
            # Start e End IGUAIS (Amarelo)
            if name == start_node or name == end_node:
                rect = pygame.Rect(0, 0, 32, 32)
                rect.center = pos
                pygame.draw.rect(self.screen, self.CLR_HUB, rect, 0, 6)
                txt = "START" if name == start_node else "END"
                lbl = self.font_hub.render(txt, True, self.CLR_HUB)

                lbl_react = lbl.get_rect(centerx=pos[0], top=pos[1] + 25)

                self.screen.blit(lbl, lbl_react)
            
            # Zonas de Custo/Risco e Normais (Quadrados)
            elif zone.zone_type == "restricted":
                rect = pygame.Rect(0, 0, 28, 28)
                rect.center = pos
                pygame.draw.rect(self.screen, self.CLR_TILE_RESTR, rect, 0, 4)
            elif zone.zone_type == "priority":
                rect = pygame.Rect(0, 0, 28, 28)
                rect.center = pos
                pygame.draw.rect(self.screen, self.CLR_TILE_PRIO, rect, 0, 4)
            elif zone.zone_type == "normal":
                rect = pygame.Rect(0, 0, 24, 24)
                rect.center = pos
                pygame.draw.rect(self.screen, self.CLR_TILE_NORMAL, rect, 0, 4)

        # 3. MOVIMENTO DO DRONE (APARECER / DESAPARECER)
        for drone in drones:
            # Desenha o drone diretamente no centro da zona atual
            draw_pos = self._scale(drone.current_zone.x, drone.current_zone.y)

            if self.drone_img:
                rect = self.drone_img.get_rect(center=(int(draw_pos[0]), int(draw_pos[1])))
                self.screen.blit(self.drone_img, rect)

            if drone.current_zone.name not in (start_node, end_node):
                id_txt = self.font_id.render(f"D{drone.drone_id}", True, (255, 255, 255))
                self.screen.blit(id_txt, (int(draw_pos[0]) - 10, int(draw_pos[1]) - 55))

        self._draw_legend()

        pygame.display.flip()
        self.clock.tick(3) # 60 FPS para o movimento não ser brusco