"""Utilitários de renderização nativa em Full HD (1920x1080) sobre o espaço lógico 960x540."""

import pygame
from config import settings

SCALE = getattr(settings, "RENDER_SCALE", 2)
_FONT_CACHE = {}


def font(size, bold=False, name="consolas"):
    """Retorna uma fonte renderizada diretamente na resolução Full HD."""
    key = (name, int(size * SCALE), bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont(name, int(size * SCALE), bold=bold)
    return _FONT_CACHE[key]


def mouse_pos():
    """Posição atual do mouse convertida da janela (1920x1080) para o espaço lógico (960x540)."""
    mx, my = pygame.mouse.get_pos()
    return mx // SCALE, my // SCALE


def scale_event(event):
    """Converte coordenadas de eventos de mouse para o espaço lógico 960x540."""
    if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
        if hasattr(event, "pos"):
            dados = dict(event.dict)
            dados["pos"] = (event.pos[0] // SCALE, event.pos[1] // SCALE)
            if "rel" in dados:
                dados["rel"] = (event.rel[0] // SCALE, event.rel[1] // SCALE)
            return pygame.event.Event(event.type, dados)
    return event


def srect(x, y=None, w=None, h=None):
    """Converte um Rect ou coordenadas lógicas (960x540) para pixels reais (1920x1080)."""
    if isinstance(x, pygame.Rect):
        return pygame.Rect(x.x * SCALE, x.y * SCALE, x.width * SCALE, x.height * SCALE)
    return pygame.Rect(int(x * SCALE), int(y * SCALE), int(w * SCALE), int(h * SCALE))


def spt(x, y):
    """Converte um ponto lógico (x, y) para pixels reais."""
    return (int(x * SCALE), int(y * SCALE))


def sdim(w, h):
    """Converte dimensões lógicas (w, h) para pixels reais."""
    return (int(w * SCALE), int(h * SCALE))


def sval(v):
    """Converte um valor escalar lógico para pixels reais."""
    return int(round(v * SCALE))
