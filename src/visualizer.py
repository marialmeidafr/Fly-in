import pygame
from models import Zone, Drone, Connection
from typing import List, Dict, Optional, Any


class Visualizer:

    def __init__(self, zones: Dict[str, Zone],
                 width: int = 1200, height: int = 800) -> None:
        pygame.init()
        pygame.display.set_caption("42_Fly-in")

        self.CLR_BG = (255, 204, 204)
        self.CLR_STD = (142, 205, 133)
        self.CLR_PRIO = (166, 199, 235)
        self.CLR_RESTR = (214, 120, 120)
        self.CLR_BORDER = (30, 30, 30)
        self.CLR_TEXT = (40, 40, 40)
        self.CLR_BLACK = (0, 0, 0)
        self.CLR_CONN_BORDER = (90, 90, 90)
        self.CLR_CONN_INNER = (150, 150, 150)

        self.screen: Any = pygame.display.set_mode((width, height))

        self.drone_img: Any = None
        self.start_img: Any = None
        self.end_img: Any = None
        self._frozen_state: Optional[Dict[str, object]] = None

        try:
            _d = pygame.image.load("assets/drone.png").convert_alpha()
            self.drone_img = pygame.transform.scale(_d, (60, 60))
            _s = pygame.image.load("assets/start.png").convert_alpha()
            self.start_img = pygame.transform.scale(_s, (120, 120))
            _e = pygame.image.load("assets/end.png").convert_alpha()
            self.end_img = pygame.transform.scale(_e, (120, 120))
        except Exception:
            pass

        self.font_id: pygame.font.Font = pygame.font.SysFont(
            "Arial", 14, bold=True)
        self.font_hub: pygame.font.Font = pygame.font.SysFont(
            "Arial", 22, bold=True)
        self.font_legend: pygame.font.Font = pygame.font.SysFont(
            "Arial", 18, bold=True)
        self.font_turn: pygame.font.Font = pygame.font.SysFont(
            "Arial", 24, bold=True)

        self.zones = zones
        self._calculate_scaling()
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.paused = True
        self.running = True
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.pan_step = 25

        self.controls_active = True

        self.simulation: Optional[Any] = None

    def attach_simulation(self, sim: Any) -> None:
        self.simulation = sim
        try:
            if hasattr(self.simulation, "paused"):
                self.simulation.paused = self.paused
        except Exception:
            pass

    def _calculate_scaling(self) -> None:
        all_x = [z.x for z in self.zones.values()]
        all_y = [z.y for z in self.zones.values()]
        self.min_x, self.max_x = min(all_x), max(all_x)
        self.min_y, self.max_y = min(all_y), max(all_y)
        self.pad = 70

    def _scale(self, x: int, y: int) -> tuple[int, int]:
        w, h = self.screen.get_size()
        rx = (self.max_x - self.min_x) or 1
        ry = (self.max_y - self.min_y) or 1
        nx = self.pad + (x - self.min_x) * (w - 2 * self.pad) // rx
        ny = self.pad + (y - self.min_y) * (h - 2 * self.pad) // ry
        nx += self.view_offset_x
        ny += self.view_offset_y
        return (int(nx), int(ny))

    def _connection_zone_names(self, conn: Connection) -> tuple[str, str]:
        if hasattr(conn, "start") and hasattr(conn, "end"):
            return conn.start, conn.end
        return conn.zone_1.name, conn.zone_2.name

    def _freeze_state(self, drones: List[Drone], connections: List[Connection],
                      turn: int, start_node: str, end_node: str) -> None:
        self._frozen_state = {
            "turn": turn,
            "start_node": start_node,
            "end_node": end_node,
            "drones": [(d.drone_id, d.current_zone.name) for d in drones],
            "connections": [self._connection_zone_names(c)
                            for c in connections],
        }

    def _handle_events(self, drones: List[Drone],
                       connections: List[Connection],
                       turn: int, start_node: str, end_node: str) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.controls_active = True

            if event.type == pygame.KEYDOWN and self.controls_active:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    if self.simulation is not None:
                        try:
                            if hasattr(self.simulation, "paused"):
                                self.simulation.paused = self.paused
                        except Exception:
                            pass

                    if self.paused:
                        self._freeze_state(
                            drones, connections, turn, start_node, end_node)
                    else:
                        self._frozen_state = None

    def draw_frame(self, drones: List[Drone],
                   connections: List[Connection], turn: int,
                   start_node: str, end_node: str) -> None:
        self._handle_events(drones, connections, turn, start_node, end_node)

        if self.paused and self._frozen_state is not None:
            turn_value = self._frozen_state.get("turn", 0)
            render_turn = turn_value if isinstance(turn_value, int) else 0
            render_start = str(self._frozen_state.get("start_node", ""))
            render_end = str(self._frozen_state.get("end_node", ""))
            render_drones: Any = self._frozen_state.get("drones", [])
            render_connections: Any = self._frozen_state.get("connections", [])
        else:
            render_turn = turn
            render_start = start_node
            render_end = end_node
            render_drones = drones
            render_connections = connections

        self.screen.fill(self.CLR_BG)

        for conn in render_connections:
            if isinstance(conn, tuple):
                start_name, end_name = conn
            else:
                start_name, end_name = self._connection_zone_names(conn)

            z1 = self.zones[start_name]
            z2 = self.zones[end_name]
            p1 = self._scale(z1.x, z1.y)
            p2 = self._scale(z2.x, z2.y)

            pygame.draw.line(self.screen, self.CLR_CONN_BORDER, p1, p2, 10)
            pygame.draw.line(self.screen, self.CLR_CONN_INNER, p1, p2, 6)

        color_map = {
            "green": (34, 177, 76),
            "blue": (121, 188, 229),
            "red":   (251, 133, 135),
            "yellow": (222, 209, 114),
            "orange": (221, 124, 65),
            "purple": (158, 105, 183),
            "black": (96, 96, 130),
            "brown": (120, 72, 40),
            "maroon": (128, 0, 0),
            "gold": (197, 184, 85),
            "darkred": (167, 85, 85),
            "violet": (203, 133, 226),
            "crimson": (213, 97, 121),
            "cyan": (103, 191, 177),
            "lime": (136, 200, 112),
            "magenta": (183, 56, 56),
            "rainbow": (255, 255, 255),
            }

        for name, zone in self.zones.items():
            pos = self._scale(zone.x, zone.y)
            is_start = (name == render_start)
            is_end = (name == render_end)

            zone_color_str = getattr(zone, "color", "white")
            color = color_map.get(zone_color_str)

            if color is None:
                color = self.CLR_STD
                if getattr(zone, "zone_type", "") == "restricted":
                    color = self.CLR_RESTR
                elif getattr(zone, "zone_type", "") == "priority":
                    color = self.CLR_PRIO
            if not is_start and not is_end:
                zone_rect = pygame.Rect(0, 0, 45, 45)
                zone_rect.center = pos
                pygame.draw.rect(self.screen, color, zone_rect, 0, 8)
                pygame.draw.rect(self.screen, self.CLR_BORDER, zone_rect, 3, 8)

            if is_start or is_end:
                img = self.start_img if is_start else self.end_img
                if img:
                    img_rect = img.get_rect(center=pos)
                    self.screen.blit(img, img_rect)
                else:
                    pygame.draw.circle(self.screen, color, pos, 30)
                    pygame.draw.circle(
                        self.screen, self.CLR_BORDER, pos, 30, 3)

                text_content = "START" if is_start else "END"
                lbl = self.font_hub.render(text_content, True, self.CLR_BLACK)
                label_top = pos[1] + (45 if is_start else 35)
                lbl_rect = lbl.get_rect(centerx=pos[0], top=label_top)
                self.screen.blit(lbl, lbl_rect)

        turn_txt = self.font_turn.render(
            f"TURN: {render_turn}", True, self.CLR_BLACK)
        self.screen.blit(turn_txt, (40, 20))

        for drone in render_drones:
            if isinstance(drone, tuple):
                drone_id, zone_name = drone
                current_zone = self.zones[zone_name]
            else:
                drone_id = drone.drone_id
                current_zone = drone.current_zone

            curr_pos = self._scale(current_zone.x, current_zone.y)
            is_hub = current_zone.name in (render_start, render_end)
            if current_zone.name == render_start:
                curr_pos = (curr_pos[0], curr_pos[1] - 20)

            if self.drone_img:
                drone_rect = self.drone_img.get_rect(center=curr_pos)
                self.screen.blit(self.drone_img, drone_rect)
            else:
                pygame.draw.circle(self.screen, (40, 40, 40), curr_pos, 15)

            if not is_hub:
                id_txt = self.font_id.render(
                    f"D{drone_id}", True, self.CLR_BORDER)
                id_rect = id_txt.get_rect(
                    centerx=curr_pos[0], bottom=curr_pos[1] - 35)
                self.screen.blit(id_txt, id_rect)

        if self.paused:
            paused_txt = self.font_turn.render("PAUSED", True, self.CLR_BLACK)
            paused_rect = paused_txt.get_rect(
                topright=(self.screen.get_width() - 40, 20))
            self.screen.blit(paused_txt, paused_rect)

        pygame.display.flip()
        self.clock.tick(2)
