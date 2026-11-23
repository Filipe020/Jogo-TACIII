"""Renderizador Full HD com lógica e interface em 960×540.

O tamanho real é Full HD quando a tela suporta 1920×1080. Se o monitor
não suporta, usa a resolução nativa para não perder a imagem.
F11 alterna entre tela cheia e janela para facilitar testes.
"""
import pygame
from config import settings


class FullscreenCanvas:
    def __init__(self):
        self.fullscreen = bool(settings.FULLSCREEN)
        self.canvas = None
        self.display = None
        self.viewport = None
        self._create_display()

    def _choose_size(self):
        try:
            desktop = pygame.display.get_desktop_sizes()[0]
        except (AttributeError, IndexError, pygame.error):
            desktop = (settings.FULLHD_WIDTH, settings.FULLHD_HEIGHT)
        # O sistema define um modo realmente suportado, com fallback nativo.
        try:
            modes = pygame.display.list_modes()
        except pygame.error:
            modes = []
        fullhd = (settings.FULLHD_WIDTH, settings.FULLHD_HEIGHT)
        return fullhd if (desktop[0] >= fullhd[0] and desktop[1] >= fullhd[1]
                          and (modes == -1 or fullhd in modes)) else desktop

    def _create_display(self):
        size = self._choose_size() if self.fullscreen else (
            settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        try:
            self.display = pygame.display.set_mode(size, flags)
        except pygame.error:
            self.display = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            self.fullscreen = False
        actual_w, actual_h = self.display.get_size()
        scale = min(actual_w / settings.SCREEN_WIDTH,
                    actual_h / settings.SCREEN_HEIGHT)
        width = max(1, round(settings.SCREEN_WIDTH * scale))
        height = max(1, round(settings.SCREEN_HEIGHT * scale))
        left = (actual_w - width) // 2
        top = (actual_h - height) // 2
        self.viewport = pygame.Rect(left, top, width, height)
        settings.DISPLAY_VIEWPORT = (left, top, width, height)
        if self.canvas is None:
            self.canvas = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)).convert()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self._create_display()

    def to_logical(self, position):
        x, y = position
        vp = self.viewport
        return (int((x - vp.left) * settings.SCREEN_WIDTH / vp.width),
                int((y - vp.top) * settings.SCREEN_HEIGHT / vp.height))

    def map_event(self, event):
        if not hasattr(event, "pos"):
            return event
        data = event.dict.copy()
        data["pos"] = self.to_logical(event.pos)
        if hasattr(event, "rel"):
            vp = self.viewport
            data["rel"] = (int(event.rel[0] * settings.SCREEN_WIDTH / vp.width),
                           int(event.rel[1] * settings.SCREEN_HEIGHT / vp.height))
        return pygame.event.Event(event.type, data)

    def present(self):
        self.display.fill((10, 8, 20))
        # nearest-neighbor para preservar sprites pixel-art sem embaçamento.
        image = pygame.transform.scale(self.canvas, self.viewport.size)
        self.display.blit(image, self.viewport.topleft)
