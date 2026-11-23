"""Editor de fases integrado ao Shadow Rebirth, operado com mouse e teclado.

Ferramentas: selecionar/mover, desenhar plataforma, inserir inimigos,
definir início do jogador, apagar; três slots JSON e teste no jogo (F5).
"""

from copy import deepcopy

import pygame

from config import settings
from levels.level_data import (
    SLOTS,
    TIPOS_INIMIGOS,
    carregar_slot,
    mapa_novo,
    mapa_padrao,
    salvar_slot,
)
from systems.display import font as scaled_font, mouse_pos, sdim, spt, srect, sval

GRID = 20
PANEL_X = 746
TOP_H = 52
BOTTOM_Y = 507
TOOLS = [
    ("selecionar", "V  Selecionar / mover"),
    ("plataforma", "1  Plataforma"),
    ("basico", "2  Inimigo basico"),
    ("rapido", "3  Inimigo rapido"),
    ("resistente", "4  Inimigo forte"),
    ("distancia", "5  Inimigo atirador"),
    ("jogador", "6  Inicio do jogador"),
    ("chefe", "7  Portal do chefe"),
    ("apagar", "X  Apagar"),
]
KEY_TO_TOOL = {
    pygame.K_v: "selecionar",
    pygame.K_1: "plataforma",
    pygame.K_2: "basico",
    pygame.K_3: "rapido",
    pygame.K_4: "resistente",
    pygame.K_5: "distancia",
    pygame.K_6: "jogador",
    pygame.K_7: "chefe",
    pygame.K_x: "apagar",
}
COLORS = {
    "basico": (217, 100, 113),
    "rapido": (241, 185, 84),
    "resistente": (139, 147, 227),
    "distancia": (114, 201, 151),
    "chefe": (210, 103, 250),
}


class LevelEditor:
    def __init__(self, background):
        self.background = background
        self.slot = 1
        self.mapa = carregar_slot(1) or mapa_padrao()
        self.dirty = False
        self.camera_x = 0.0
        self.tool = "selecionar"
        self.dragging = None
        self.move_logged = False
        self.platform_start = None
        self.undo_stack = []
        self.redo_stack = []
        self.notice = "Selecione uma ferramenta para editar o mapa."
        self.notice_time = 7.0
        self.confirm_action = None
        self.show_grid = True
        self.font = scaled_font(16)
        self.font_small = scaled_font(13)
        self.font_bold = scaled_font(17, bold=True)
        self.font_title = scaled_font(22, bold=True)

        self.tool_buttons = [
            pygame.Rect(PANEL_X + 10, 90 + i * 27, 194, 25)
            for i in range(len(TOOLS))
        ]
        self.spawn_button = pygame.Rect(PANEL_X + 10, 336, 194, 26)
        self.action_buttons = {
            "salvar": pygame.Rect(PANEL_X + 10, 369, 94, 28),
            "carregar": pygame.Rect(PANEL_X + 110, 369, 94, 28),
            "testar": pygame.Rect(PANEL_X + 10, 403, 194, 32),
            "novo": pygame.Rect(PANEL_X + 10, 441, 194, 28),
        }
        self.slots_buttons = {
            i: pygame.Rect(333 + (i - 1) * 105, 9, 99, 33) for i in SLOTS
        }
        self.width_minus = pygame.Rect(651, 9, 29, 32)
        self.width_plus = pygame.Rect(689, 9, 29, 32)
        self.back_button = pygame.Rect(PANEL_X + 10, 9, 194, 33)

    def informar(self, text, seconds=4):
        self.notice = text
        self.notice_time = seconds

    def _registrar_alteracao(self):
        self.undo_stack.append(deepcopy(self.mapa))
        if len(self.undo_stack) > 40:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.dirty = True
        self.confirm_action = None

    def desfazer(self):
        if self.undo_stack:
            self.redo_stack.append(deepcopy(self.mapa))
            self.mapa = self.undo_stack.pop()
            self._limitar_camera()
            self.dirty = True
            self.informar("Alteracao desfeita (Ctrl+Y refaz).")

    def refazer(self):
        if self.redo_stack:
            self.undo_stack.append(deepcopy(self.mapa))
            self.mapa = self.redo_stack.pop()
            self._limitar_camera()
            self.dirty = True
            self.informar("Alteracao refeita.")

    def _limitar_camera(self):
        self.camera_x = max(0, min(self.camera_x, self.mapa["largura"] - PANEL_X))

    def _em_mapa(self, pos):
        return 0 <= pos[0] < PANEL_X and TOP_H <= pos[1] < BOTTOM_Y

    def _mundo(self, pos):
        return int(pos[0] + self.camera_x), int(pos[1])

    def _snap(self, pos):
        mx, my = self._mundo(pos)
        return (mx // GRID) * GRID, (my // GRID) * GRID

    def _hit(self, pos):
        """Prioriza o ícone do jogador e inimigos em relação às plataformas."""
        wx, wy = self._mundo(pos)
        x, y = self.mapa["spawn_jogador"]
        if pygame.Rect(x - 4, y - 4, 36, 52).collidepoint(wx, wy):
            return "jogador", None
        for i in range(len(self.mapa["inimigos"]) - 1, -1, -1):
            e = self.mapa["inimigos"][i]
            if pygame.Rect(
                e["x"] - 5,
                e["y"] - 5,
                86 if e["tipo"] == "chefe" else 35,
                104 if e["tipo"] == "chefe" else 44,
            ).collidepoint(wx, wy):
                return "inimigo", i
        for i in range(len(self.mapa["plataformas"]) - 1, -1, -1):
            if pygame.Rect(*self.mapa["plataformas"][i]).collidepoint(wx, wy):
                return "plataforma", i
        return None

    def _apagar(self, pos):
        alvo = self._hit(pos)
        if alvo is None:
            return
        tipo, idx = alvo
        if tipo == "jogador":
            self.informar("O inicio do jogador nao pode ser apagado; use a ferramenta 6.")
            return
        self._registrar_alteracao()
        if tipo == "inimigo":
            self.mapa["inimigos"].pop(idx)
        else:
            self.mapa["plataformas"].pop(idx)
        self.informar("Elemento apagado. Ctrl+Z desfaz.")

    def _inserir(self, pos):
        x, y = self._snap(pos)
        x = max(0, min(x, self.mapa["largura"] - GRID * 2))
        if self.tool in TIPOS_INIMIGOS:
            if len(self.mapa["inimigos"]) >= 200:
                self.informar("Limite de 200 inimigos por fase.")
                return
            self._registrar_alteracao()
            altura = 94 if self.tool == "chefe" else 48
            self.mapa["inimigos"].append({
                "tipo": self.tool,
                "x": x,
                "y": max(0, min(y, settings.SCREEN_HEIGHT - altura)),
            })
        elif self.tool == "jogador":
            self._registrar_alteracao()
            self.mapa["spawn_jogador"] = [
                max(0, min(x, self.mapa["largura"] - 28)),
                max(0, min(y, settings.SCREEN_HEIGHT - 44)),
            ]

    def _iniciar_movimento(self, pos):
        alvo = self._hit(pos)
        if alvo is None:
            return
        tipo, index = alvo
        wx, wy = self._mundo(pos)
        if tipo == "jogador":
            x, y = self.mapa["spawn_jogador"]
        elif tipo == "inimigo":
            x, y = self.mapa["inimigos"][index]["x"], self.mapa["inimigos"][index]["y"]
        else:
            x, y = self.mapa["plataformas"][index][:2]
        self.dragging = (tipo, index, wx - x, wy - y)
        self.move_logged = False

    def _arrastar(self, pos):
        if self.dragging is None:
            return
        tipo, index, dx, dy = self.dragging
        wx, wy = self._mundo(pos)
        newx, newy = ((wx - dx) // GRID) * GRID, ((wy - dy) // GRID) * GRID
        if tipo == "jogador":
            target = self.mapa["spawn_jogador"]
            w, h = 28, 44
        elif tipo == "inimigo":
            target = self.mapa["inimigos"][index]
            w, h = (76, 94) if target["tipo"] == "chefe" else (35, 48)
        else:
            target = self.mapa["plataformas"][index]
            w, h = target[2], target[3]
        newx = max(0, min(newx, self.mapa["largura"] - w))
        newy = max(0, min(newy, settings.SCREEN_HEIGHT - h))
        if tipo == "inimigo":
            changed = target["x"] != newx or target["y"] != newy
        else:
            changed = target[0] != newx or target[1] != newy
        if changed and not self.move_logged:
            self._registrar_alteracao()
            self.move_logged = True
        if tipo == "inimigo":
            target["x"], target["y"] = newx, newy
        else:
            target[0], target[1] = newx, newy

    def _finalizar_plataforma(self, pos):
        if self.platform_start is None:
            return
        if len(self.mapa["plataformas"]) >= 500:
            self.informar("Limite de 500 plataformas por fase.")
            self.platform_start = None
            return
        ax, ay = self.platform_start
        bx, by = self._snap(pos)
        x, y = min(ax, bx), min(ay, by)
        w = max(40, abs(ax - bx) + GRID)
        h = max(20, abs(ay - by) + GRID)
        x = max(0, min(x, self.mapa["largura"] - GRID))
        y = max(0, min(y, settings.SCREEN_HEIGHT - GRID))
        w = min(w, self.mapa["largura"] - x)
        h = min(h, settings.SCREEN_HEIGHT - y)
        if w > 0 and h > 0:
            self._registrar_alteracao()
            self.mapa["plataformas"].append([x, y, w, h])
        self.platform_start = None

    def salvar(self):
        try:
            salvar_slot(self.slot, self.mapa)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            self.informar(f"Erro ao salvar: {exc}", 7)
            return False
        self.dirty = False
        self.informar(f"Fase {self.slot} salva em levels/custom_level_{self.slot:02}.json")
        return True

    def _precisa_confirmacao(self, acao):
        if not self.dirty:
            self.confirm_action = None
            return False
        if self.confirm_action == acao:
            self.confirm_action = None
            return False
        self.confirm_action = acao
        self.informar("Alteracoes nao salvas! Repita a acao para descartar, ou Ctrl+S para salvar.", 8)
        return True

    def carregar(self):
        if self._precisa_confirmacao("carregar"):
            return
        try:
            self.mapa = carregar_slot(self.slot) or mapa_padrao()
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self.informar(f"Erro ao carregar fase: {exc}", 7)
            return
        self.dirty = False
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._limitar_camera()
        self.informar(f"Fase {self.slot} carregada.")

    def mudar_slot(self, slot):
        if slot == self.slot:
            return
        if self.dirty:
            self.informar("Salve a fase atual (Ctrl+S) antes de mudar de slot.", 6)
            return
        try:
            mapa = carregar_slot(slot) or mapa_novo()
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self.informar(f"Erro ao carregar a fase {slot}: {exc}", 7)
            return
        self.slot = slot
        self.mapa = mapa
        self.camera_x = 0
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.confirm_action = None
        self.informar(f"Fase {slot} selecionada. F5 testa; Ctrl+S salva.")

    def novo(self):
        if self._precisa_confirmacao("novo"):
            return
        self._registrar_alteracao()
        self.mapa = mapa_novo()
        self.camera_x = 0
        self.informar("Mapa novo criado. Edite e salve com Ctrl+S.")

    def mudar_largura(self, delta):
        antiga = self.mapa["largura"]
        nova = max(settings.SCREEN_WIDTH, min(12000, antiga + delta))
        if nova == antiga:
            return
        for p in self.mapa["plataformas"]:
            if p[0] + p[2] > nova:
                self.informar("Mova plataformas do fim antes de encurtar a fase.")
                return
        if (
            any(e["x"] + (76 if e["tipo"] == "chefe" else 35) > nova for e in self.mapa["inimigos"])
            or self.mapa["spawn_jogador"][0] + 28 > nova
        ):
            self.informar("Mova inimigos e jogador antes de encurtar a fase.")
            return
        self._registrar_alteracao()
        self.mapa["largura"] = nova
        self._limitar_camera()
        self.informar(f"Largura do mapa: {nova}px")

    def _voltar_ao_menu(self):
        """Pede confirmação antes de descartar alterações não salvas."""
        if self._precisa_confirmacao("menu"):
            return None
        self.dragging = None
        self.platform_start = None
        return "menu"

    def executar_acao(self, acao):
        if acao == "salvar":
            self.salvar()
        elif acao == "carregar":
            self.carregar()
        elif acao == "novo":
            self.novo()
        elif acao == "testar":
            return "testar"
        return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            ctrl = bool(event.mod & pygame.KMOD_CTRL)
            if ctrl and event.key == pygame.K_s:
                self.salvar()
            elif ctrl and event.key == pygame.K_o:
                self.carregar()
            elif ctrl and event.key == pygame.K_z:
                self.desfazer()
            elif ctrl and event.key == pygame.K_y:
                self.refazer()
            elif event.key == pygame.K_ESCAPE:
                return self._voltar_ao_menu()
            elif event.key == pygame.K_F5:
                return "testar"
            elif event.key in (pygame.K_F1, pygame.K_F2, pygame.K_F3):
                self.mudar_slot(event.key - pygame.K_F1 + 1)
            elif event.key in KEY_TO_TOOL:
                self.tool = KEY_TO_TOOL[event.key]
            elif event.key == pygame.K_b:
                self._registrar_alteracao()
                self.mapa["spawn_automatico"] = not self.mapa["spawn_automatico"]
            elif event.key == pygame.K_g:
                self.show_grid = not self.show_grid
            elif event.key == pygame.K_n:
                self.novo()
            elif event.key == pygame.K_LEFTBRACKET:
                self.mudar_largura(-400)
            elif event.key == pygame.K_RIGHTBRACKET:
                self.mudar_largura(400)

        elif event.type == pygame.MOUSEWHEEL:
            self.camera_x -= event.y * 160
            self._limitar_camera()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if event.button == 1:
                if self.back_button.collidepoint(pos):
                    return self._voltar_ao_menu()
                for slot, rect in self.slots_buttons.items():
                    if rect.collidepoint(pos):
                        self.mudar_slot(slot)
                        return None
                if self.width_minus.collidepoint(pos):
                    self.mudar_largura(-400)
                    return None
                if self.width_plus.collidepoint(pos):
                    self.mudar_largura(400)
                    return None
                for (tool, _label), rect in zip(TOOLS, self.tool_buttons):
                    if rect.collidepoint(pos):
                        self.tool = tool
                        return None
                if self.spawn_button.collidepoint(pos):
                    self._registrar_alteracao()
                    self.mapa["spawn_automatico"] = not self.mapa["spawn_automatico"]
                    return None
                for acao, rect in self.action_buttons.items():
                    if rect.collidepoint(pos):
                        return self.executar_acao(acao)
                if self._em_mapa(pos):
                    if self.tool == "plataforma":
                        self.platform_start = self._snap(pos)
                    elif self.tool == "apagar":
                        self._apagar(pos)
                    elif self.tool == "selecionar":
                        self._iniciar_movimento(pos)
                    else:
                        self._inserir(pos)
            elif event.button == 3 and self._em_mapa(pos):
                self._apagar(pos)
            elif event.button == 4:
                self.camera_x -= 160
                self._limitar_camera()
            elif event.button == 5:
                self.camera_x += 160
                self._limitar_camera()

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._arrastar(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.platform_start is not None:
                self._finalizar_plataforma(event.pos)
            self.dragging = None
            self.move_logged = False
        return None

    def update(self, dt):
        teclas = pygame.key.get_pressed()
        desloc = 650 * (2 if teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT] else 1) * dt
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.camera_x += desloc
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.camera_x -= desloc
        self._limitar_camera()
        self.notice_time = max(0, self.notice_time - dt)

    def _texto(self, screen, text, x, y, color=(239, 236, 245), font=None):
        rendered = (font or self.font).render(str(text), True, color)
        screen.blit(rendered, spt(x, y))

    def _draw_grid(self, screen):
        xoffset = int(self.camera_x) % GRID
        for x in range(-xoffset, PANEL_X, GRID):
            c = (69, 60, 97) if (int(x + self.camera_x) // GRID) % 5 else (97, 84, 127)
            pygame.draw.line(screen, c, spt(x, TOP_H), spt(x, BOTTOM_Y), sval(1))
        for y in range((TOP_H // GRID) * GRID, BOTTOM_Y, GRID):
            c = (69, 60, 97) if (y // GRID) % 5 else (97, 84, 127)
            pygame.draw.line(screen, c, spt(0, y), spt(PANEL_X, y), sval(1))

    def _draw_enemy(self, screen, x, y, tipo, ghost=False):
        color = COLORS[tipo]
        if tipo == "chefe":
            pygame.draw.ellipse(screen, (44, 21, 79), srect(x, y + 2, 68, 82))
            pygame.draw.ellipse(screen, color, srect(x, y + 2, 68, 82), sval(3))
            pygame.draw.ellipse(screen, (174, 104, 255), srect(x + 12, y + 14, 44, 62), sval(2))
            for dy in (28, 46, 64):
                pygame.draw.line(
                    screen,
                    (243, 211, 255),
                    spt(x + 25, y + dy),
                    spt(x + 43, y + dy + 4),
                    sval(2),
                )
            if not ghost:
                self._texto(screen, "PORTAL", x - 3, y - 18, color, self.font_small)
            return
        pygame.draw.circle(screen, color, spt(x + 13, y + 10), sval(10))
        pygame.draw.rect(screen, color, srect(x + 6, y + 19, 15, 17), border_radius=sval(4))
        pygame.draw.line(screen, color, spt(x + 8, y + 34), spt(x + 4, y + 42), sval(3))
        pygame.draw.line(screen, color, spt(x + 20, y + 34), spt(x + 24, y + 42), sval(3))
        pygame.draw.circle(screen, (26, 22, 42), spt(x + 9, y + 9), sval(2))
        pygame.draw.circle(screen, (26, 22, 42), spt(x + 17, y + 9), sval(2))
        if not ghost:
            self._texto(screen, tipo[:3].upper(), x - 4, y - 16, color, self.font_small)

    def _draw_world(self, screen):
        self.background.draw(screen, self.camera_x)
        veil = pygame.Surface(sdim(PANEL_X, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((12, 11, 24, 95))
        screen.blit(veil, (0, 0))

        old_clip = screen.get_clip()
        screen.set_clip(srect(0, TOP_H, PANEL_X, BOTTOM_Y - TOP_H))
        if self.show_grid:
            self._draw_grid(screen)
        cam = int(self.camera_x)
        for x, y, w, h in self.mapa["plataformas"]:
            r = pygame.Rect(x - cam, y, w, h)
            if r.right < 0 or r.left > PANEL_X:
                continue
            pygame.draw.rect(screen, settings.COLOR_PLATFORM, srect(r))
            pygame.draw.rect(screen, settings.COLOR_PLATFORM_TOP, srect(r.x, r.y, r.width, min(6, h)))
            pygame.draw.rect(screen, (177, 140, 106), srect(r), sval(1))
        for e in self.mapa["inimigos"]:
            if -40 <= e["x"] - cam <= PANEL_X + 20:
                self._draw_enemy(screen, e["x"] - cam, e["y"], e["tipo"])
        sx, sy = self.mapa["spawn_jogador"]
        pygame.draw.rect(screen, (89, 220, 209), srect(sx - cam, sy, 28, 44), sval(2))
        pygame.draw.circle(screen, (89, 220, 209), spt(sx - cam + 14, sy + 10), sval(7))
        self._texto(screen, "START", sx - cam - 10, sy - 18, (127, 244, 231), self.font_small)

        mouse = mouse_pos()
        if self.platform_start is not None:
            ax, ay = self.platform_start
            bx, by = self._snap(mouse)
            r = pygame.Rect(
                min(ax, bx) - cam,
                min(ay, by),
                max(40, abs(ax - bx) + GRID),
                max(20, abs(ay - by) + GRID),
            )
            pygame.draw.rect(screen, (228, 210, 143), srect(r), sval(2))
        elif self._em_mapa(mouse) and self.tool in TIPOS_INIMIGOS:
            x, y = self._snap(mouse)
            self._draw_enemy(screen, x - cam, y, self.tool, ghost=True)
        elif self._em_mapa(mouse) and self.tool == "jogador":
            x, y = self._snap(mouse)
            pygame.draw.rect(screen, (127, 244, 231), srect(x - cam, y, 28, 44), sval(2))
        elif self._em_mapa(mouse) and self.tool == "plataforma":
            x, y = self._snap(mouse)
            pygame.draw.rect(screen, (228, 210, 143), srect(x - cam, y, 40, GRID), sval(2))
        elif self._em_mapa(mouse) and self.tool in ("selecionar", "apagar"):
            alvo = self._hit(mouse)
            if alvo:
                tipo, index = alvo
                if tipo == "plataforma":
                    x, y, w, h = self.mapa["plataformas"][index]
                    r = pygame.Rect(x - cam, y, w, h)
                elif tipo == "jogador":
                    x, y = self.mapa["spawn_jogador"]
                    r = pygame.Rect(x - cam, y, 28, 44)
                else:
                    e = self.mapa["inimigos"][index]
                    r = pygame.Rect(
                        e["x"] - cam,
                        e["y"],
                        76 if e["tipo"] == "chefe" else 28,
                        94 if e["tipo"] == "chefe" else 44,
                    )
                pygame.draw.rect(
                    screen,
                    (250, 214, 104) if self.tool == "selecionar" else (255, 115, 120),
                    srect(r.inflate(4, 4)),
                    sval(2),
                )
        screen.set_clip(old_clip)
        pygame.draw.line(
            screen,
            (157, 121, 201),
            spt(PANEL_X - 1, 0),
            spt(PANEL_X - 1, settings.SCREEN_HEIGHT),
            sval(2),
        )

    def _rounded_button(self, screen, rect, title, active=False, accent=False):
        drect = srect(rect)
        color = (88, 58, 127) if active else (47, 43, 65)
        if accent:
            color = (107, 61, 149)
        pygame.draw.rect(screen, color, drect, border_radius=sval(6))
        pygame.draw.rect(
            screen,
            (161, 127, 200) if active or accent else (84, 75, 103),
            drect,
            sval(1),
            border_radius=sval(6),
        )
        fonte = self.font_small
        label = fonte.render(title, True, (250, 248, 253))
        if label.get_width() > drect.width - sval(12):
            fonte = scaled_font(max(10, int(13 * (drect.width - sval(12)) / label.get_width())))
            label = fonte.render(title, True, (250, 248, 253))
        if label.get_width() > drect.width - sval(10):
            label = pygame.transform.smoothscale(label, (drect.width - sval(10), label.get_height()))
        screen.blit(label, label.get_rect(center=drect.center))

    def draw(self, screen):
        self._draw_world(screen)
        pygame.draw.rect(screen, (22, 19, 36), srect(0, 0, settings.SCREEN_WIDTH, TOP_H))
        pygame.draw.line(
            screen,
            (113, 79, 153),
            spt(0, TOP_H - 1),
            spt(settings.SCREEN_WIDTH, TOP_H - 1),
            sval(2),
        )
        self._texto(screen, "EDITOR DE FASES", 12, 8, (222, 158, 255), self.font_title)
        self._texto(screen, f"{self.mapa['largura']} px", 225, 16, (190, 175, 212), self.font_small)
        for slot, rect in self.slots_buttons.items():
            self._rounded_button(screen, rect, f"F{slot}  FASE {slot}", slot == self.slot)
        self._rounded_button(screen, self.width_minus, "-")
        self._rounded_button(screen, self.width_plus, "+")
        self._rounded_button(screen, self.back_button, "< VOLTAR AO MENU", accent=True)

        pygame.draw.rect(screen, (27, 24, 43), srect(PANEL_X, TOP_H, 214, settings.SCREEN_HEIGHT - TOP_H))
        self._texto(screen, "FERRAMENTAS", PANEL_X + 14, 65, (226, 181, 249), self.font_bold)
        for (tool, label), rect in zip(TOOLS, self.tool_buttons):
            self._rounded_button(screen, rect, label, tool == self.tool)
        self._rounded_button(
            screen,
            self.spawn_button,
            f"B  Spawn automatico: {'SIM' if self.mapa['spawn_automatico'] else 'NAO'}",
            self.mapa["spawn_automatico"],
        )
        self._rounded_button(screen, self.action_buttons["salvar"], "Ctrl+S Salvar")
        self._rounded_button(screen, self.action_buttons["carregar"], "Ctrl+O Abrir")
        self._rounded_button(screen, self.action_buttons["testar"], "F5  TESTAR A FASE", accent=True)
        self._rounded_button(screen, self.action_buttons["novo"], "N  Nova fase")
        self._texto(screen, "ESC: voltar | G: grade", PANEL_X + 14, 483, (186, 175, 202), self.font_small)

        pygame.draw.rect(
            screen,
            (22, 19, 36),
            srect(0, BOTTOM_Y, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - BOTTOM_Y),
        )
        pygame.draw.line(
            screen,
            (113, 79, 153),
            spt(0, BOTTOM_Y),
            spt(settings.SCREEN_WIDTH, BOTTOM_Y),
            sval(2),
        )
        if self.notice_time > 0:
            texto = self.notice
        else:
            texto = "A/D: mover camera  |  Mouse: editar  |  Direito: apagar  |  Ctrl+Z/Y: desfazer/refazer"
        while self.font_small.size(texto)[0] > sval(PANEL_X - 25) and len(texto) > 6:
            texto = texto[:-2]
        self._texto(screen, texto, 12, 516, (232, 218, 247), self.font_small)
        mark = " *" if self.dirty else ""
        self._texto(
            screen,
            f"Fase {self.slot}{mark}",
            PANEL_X + 16,
            515,
            (250, 200, 141) if self.dirty else (127, 234, 176),
            self.font_small,
        )