"""Renderizador Full HD nativo (1920x1080) com lógica e interface em 960x540."""

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
        try:
            modes = pygame.display.list_modes()
        except pygame.error:
            modes = []
        fullhd = (settings.FULLHD_WIDTH, settings.FULLHD_HEIGHT)
        return fullhd if (
            desktop[0] >= fullhd[0]
            and desktop[1] >= fullhd[1]
            and (modes == -1 or fullhd in modes)
        ) else desktop

    def _create_display(self):
        size = self._choose_size() if self.fullscreen else (
            settings.FULLHD_WIDTH, settings.FULLHD_HEIGHT
        )
        flags = pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE
        try:
            self.display = pygame.display.set_mode(size, flags)
        except pygame.error:
            self.display = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            self.fullscreen = False

        actual_w, actual_h = self.display.get_size()
        scale = min(actual_w / settings.FULLHD_WIDTH, actual_h / settings.FULLHD_HEIGHT)
        width = max(1, round(settings.FULLHD_WIDTH * scale))
        height = max(1, round(settings.FULLHD_HEIGHT * scale))
        left = (actual_w - width) // 2
        top = (actual_h - height) // 2
        self.viewport = pygame.Rect(left, top, width, height)
        settings.DISPLAY_VIEWPORT = (left, top, width, height)

        if self.canvas is None:
            self.canvas = pygame.Surface(
                (settings.FULLHD_WIDTH, settings.FULLHD_HEIGHT)
            ).convert()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        settings.FULLSCREEN = self.fullscreen
        self._create_display()

    def handle_resize(self, size):
        if not self.fullscreen:
            self.display = pygame.display.set_mode(size, pygame.RESIZABLE)
            actual_w, actual_h = self.display.get_size()
            scale = min(actual_w / settings.FULLHD_WIDTH, actual_h / settings.FULLHD_HEIGHT)
            width = max(1, round(settings.FULLHD_WIDTH * scale))
            height = max(1, round(settings.FULLHD_HEIGHT * scale))
            left = (actual_w - width) // 2
            top = (actual_h - height) // 2
            self.viewport = pygame.Rect(left, top, width, height)
            settings.DISPLAY_VIEWPORT = (left, top, width, height)

    def to_logical(self, position):
        x, y = position
        vp = self.viewport
        return (
            int((x - vp.left) * settings.SCREEN_WIDTH / max(1, vp.width)),
            int((y - vp.top) * settings.SCREEN_HEIGHT / max(1, vp.height)),
        )

    def map_event(self, event):
        if not hasattr(event, "pos"):
            return event
        data = event.dict.copy()
        data["pos"] = self.to_logical(event.pos)
        if hasattr(event, "rel"):
            vp = self.viewport
            data["rel"] = (
                int(event.rel[0] * settings.SCREEN_WIDTH / max(1, vp.width)),
                int(event.rel[1] * settings.SCREEN_HEIGHT / max(1, vp.height)),
            )
        return pygame.event.Event(event.type, data)

    def present(self):
        if self.viewport.size == self.canvas.get_size() and self.viewport.topleft == (0, 0):
            self.display.blit(self.canvas, (0, 0))
            return
        self.display.fill((10, 8, 20))
        image = pygame.transform.smoothscale(self.canvas, self.viewport.size)
        self.display.blit(image, self.viewport.topleft)