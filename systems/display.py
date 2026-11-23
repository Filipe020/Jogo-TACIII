"""Utilitários de renderização nativa em Full HD (1920x1080) sobre o espaço lógico 960x540."""

import pygame
from config import settings

SCALE = getattr(settings, "RENDER_SCALE", 2)
_FONT_CACHE = {}


def font(size, bold=False, name="consolas"):
    """Retorna uma fonte renderizada diretamente na resolução Full HD."""
    key = (name, int(round(size * SCALE)), bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont(name, int(round(size * SCALE)), bold=bold)
    return _FONT_CACHE[key]


def mouse_pos():
    """Posição atual do mouse convertida da janela física para o espaço lógico (960x540)."""
    mx, my = pygame.mouse.get_pos()
    vx, vy, vw, vh = getattr(
        settings, "DISPLAY_VIEWPORT", (0, 0, settings.FULLHD_WIDTH, settings.FULLHD_HEIGHT)
    )
    lx = int((mx - vx) * settings.SCREEN_WIDTH / max(1, vw))
    ly = int((my - vy) * settings.SCREEN_HEIGHT / max(1, vh))
    return lx, ly


def scale_event(event):
    """Converte coordenadas de eventos de mouse para o espaço lógico 960x540."""
    if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
        if hasattr(event, "pos"):
            vx, vy, vw, vh = getattr(
                settings, "DISPLAY_VIEWPORT", (0, 0, settings.FULLHD_WIDTH, settings.FULLHD_HEIGHT)
            )
            dados = dict(event.dict)
            dados["pos"] = (
                int((event.pos[0] - vx) * settings.SCREEN_WIDTH / max(1, vw)),
                int((event.pos[1] - vy) * settings.SCREEN_HEIGHT / max(1, vh)),
            )
            if "rel" in dados:
                dados["rel"] = (
                    int(event.rel[0] * settings.SCREEN_WIDTH / max(1, vw)),
                    int(event.rel[1] * settings.SCREEN_HEIGHT / max(1, vh)),
                )
            return pygame.event.Event(event.type, dados)
    return event


def srect(x, y=None, w=None, h=None):
    """Converte um Rect ou coordenadas lógicas (960x540) para pixels reais (1920x1080)."""
    if isinstance(x, pygame.Rect):
        return pygame.Rect(
            int(round(x.x * SCALE)),
            int(round(x.y * SCALE)),
            int(round(x.width * SCALE)),
            int(round(x.height * SCALE)),
        )
    return pygame.Rect(
        int(round(x * SCALE)),
        int(round(y * SCALE)),
        int(round(w * SCALE)),
        int(round(h * SCALE)),
    )


def spt(x, y):
    """Converte um ponto lógico (x, y) para pixels reais."""
    return (int(round(x * SCALE)), int(round(y * SCALE)))


def sdim(w, h):
    """Converte dimensões lógicas (w, h) para pixels reais."""
    return (int(round(w * SCALE)), int(round(h * SCALE)))


def sval(v):
    """Converte um valor escalar lógico para pixels reais."""
    return int(round(v * SCALE))