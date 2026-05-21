import pygame
from models import Zone, Drone, Connection
from typing import List, Dict


class Visualizer:
    def __init__(self, zones: Dict[str, Zone],
                 width: int = 1200, height: int = 800):
        pygame.init()
        pygame.display.set_caption("42 Fly-in: Cozy Fleet Command")

        # --- PALETA DE CORES DO TEU ESBOÇO ---
        self.CLR_BG = (255, 204, 204)
        self.CLR_STD = (142, 205, 133)
        self.CLR_PRIO = (166, 199, 235)
        self.CLR_RESTR = (214, 120, 120)
        self.CLR_BORDER = (30, 30, 30)
        self.CLR_TEXT = (40, 40, 40)
        self.CLR_BLACK = (0, 0, 0)
        self.CLR_CONN_BORDER = (90, 90, 90)
        self.CLR_CONN_INNER = (150, 150, 150)

        self.screen = pygame.display.set_mode((width, height))

        try:
            self.drone_img = pygame.image.load(
                "assets/drone.png").convert_alpha()
            self.drone_img = pygame.transform.scale(self.drone_img, (60, 60))

            self.start_img = pygame.image.load(
                "assets/start.png").convert_alpha()
            self.start_img = pygame.transform.scale(self.start_img, (120, 120))

            self.end_img = pygame.image.load(
                "assets/end.png").convert_alpha()
            self.end_img = pygame.transform.scale(self.end_img, (120, 120))
        except Exception:
            print("No images")
            self.drone_img = None
            self.start_img = None
            self.end_img = None

        self.font_id = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_hub = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_legend = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_turn = pygame.font.SysFont("Arial", 24, bold=True)

        self.zones = zones
        self._calculate_scaling()
        self.clock = pygame.time.Clock()

    def _calculate_scaling(self) -> None:
        all_x = [z.x for z in self.zones.values()]
        all_y = [z.y for z in self.zones.values()]
        self.min_x, self.max_x = min(all_x), max(all_x)
        self.min_y, self.max_y = min(all_y), max(all_y)
        self.pad = 150

    def _scale(self, x: int, y: int) -> tuple[int, int]:
        w, h = self.screen.get_size()
        rx = (self.max_x - self.min_x) or 1
        ry = (self.max_y - self.min_y) or 1
        nx = self.pad + (x - self.min_x) * (w - 2 * self.pad) // rx
        ny = self.pad + (y - self.min_y) * (h - 2 * self.pad) // ry
        return (int(nx), int(ny))

    def draw_legend(self) -> None:
        """Desenha a legenda no canto inferior esquerdo como no teu esboço."""
        start_x, start_y = 40, self.screen.get_height() - 140
        items = [
            (self.CLR_STD, "Standard"),
            (self.CLR_PRIO, "Priority"),
            (self.CLR_RESTR, "Restricted")
        ]

        for i, (color, text) in enumerate(items):
            y_pos = start_y + (i * 35)
            # Quadrado da legenda
            rect = pygame.Rect(start_x, y_pos, 25, 25)
            pygame.draw.rect(self.screen, color, rect, 0, 5)
            pygame.draw.rect(self.screen, self.CLR_BORDER, rect, 2, 5)
            # Texto da legenda
            lbl = self.font_legend.render(text, True, self.CLR_TEXT)
            self.screen.blit(lbl, (start_x + 35, y_pos))

    def _connection_zone_names(self, conn: Connection) -> tuple[str, str]:
        """Resolve os nomes das zonas ligados pela conexão."""
        if hasattr(conn, "start") and hasattr(conn, "end"):
            return conn.start, conn.end
        return conn.zone_1.name, conn.zone_2.name

    def draw_frame(self, drones: List[Drone],
                   connections: List[Connection], turn: int,
                   start_node: str, end_node: str) -> None:
        self.screen.fill(self.CLR_BG)

        # 1. DESENHAR LINHAS (Estilo "Tubo" com borda preta)
        for conn in connections:
            start_name, end_name = self._connection_zone_names(conn)
            z1 = self.zones[start_name]
            z2 = self.zones[end_name]
            p1 = self._scale(z1.x, z1.y)
            p2 = self._scale(z2.x, z2.y)

            pygame.draw.line(self.screen, self.CLR_CONN_BORDER, p1, p2, 10)
            pygame.draw.line(self.screen, self.CLR_CONN_INNER, p1, p2, 6)

        # 2. ZONAS (Quadrados arredondados com bordas)
        for name, zone in self.zones.items():
            pos = self._scale(zone.x, zone.y)
            is_start = (name == start_node)
            is_end = (name == end_node)

            if not is_start and not is_end:
                color = self.CLR_STD
                if zone.zone_type == "restricted":
                    color = self.CLR_RESTR
                elif zone.zone_type == "priority":
                    color = self.CLR_PRIO

                rect = pygame.Rect(0, 0, 45, 45)
                rect.center = pos
                pygame.draw.rect(self.screen, color, rect, 0, 8)
                pygame.draw.rect(self.screen, self.CLR_BORDER, rect, 3, 8)

            if is_start or is_end:
                img = self.start_img if is_start else self.end_img

                if img:
                    img_rect = img.get_rect(center=pos)
                    self.screen.blit(img, img_rect)
                else:
                    pygame.draw.circle(self.screen, (200, 200, 220), pos, 30)
                    pygame.draw.circle(self.screen,
                                       self.CLR_BORDER, pos, 30, 3)

                text_content = "START" if is_start else "END"
                txt_color = self.CLR_BLACK
                lbl = self.font_hub.render(text_content, True, txt_color)
                label_top = pos[1] + (45 if is_start else 35)
                lbl_rect = lbl.get_rect(centerx=pos[0], top=label_top)
                self.screen.blit(lbl, lbl_rect)

        self.draw_legend()
        turn_txt = self.font_turn.render(f"TURN: {turn}", True, self.CLR_BLACK)
        self.screen.blit(turn_txt, (40, 20))

        for drone in drones:
            curr_pos = self._scale(drone.current_zone.x, drone.current_zone.y)
            is_hub = drone.current_zone.name in (start_node, end_node)
            if drone.current_zone.name == start_node:
                curr_pos = (curr_pos[0], curr_pos[1] - 20)

            if self.drone_img:
                rect = self.drone_img.get_rect(center=curr_pos)
                self.screen.blit(self.drone_img, rect)
            else:
                pygame.draw.circle(self.screen, (40, 40, 40), curr_pos, 15)

            if not is_hub:
                id_txt = self.font_id.render(f"D{drone.drone_id}",
                                             True, self.CLR_BORDER)
                id_rect = id_txt.get_rect(centerx=curr_pos[0],
                                          bottom=curr_pos[1] - 35)
                self.screen.blit(id_txt, id_rect)

        pygame.display.flip()
        self.clock.tick(5)
