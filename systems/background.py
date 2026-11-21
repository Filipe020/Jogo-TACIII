"""Cenário noturno usado no jogo e no editor; funciona sem o PNG se faltar."""
import os

import pygame

from config import settings


class TempleBackground:
    def __init__(self):
        caminho = getattr(
            settings,
            "COMBAT_BACKGROUND",
            os.path.join(settings.BASE_DIR, "assets", "backgrounds", "templo_noite.png"),
        )
        self.imagem = None
        if os.path.exists(caminho):
            try:
                origem = pygame.image.load(caminho).convert()
                # Uma folga horizontal permite movimento sutil de paralaxe sem lacunas.
                # Mantém o aspecto 16:9; a borda extra serve para paralaxe.
                self.imagem = pygame.transform.smoothscale(origem, (1120, 630))
            except pygame.error:
                pass

    def draw(self, surface, camera_x=0):
        surface.fill(settings.COLOR_BG)
        if self.imagem:
            deslocamento = min(160, max(0, int(camera_x * 0.06)))
            surface.blit(self.imagem, (-deslocamento, -45))
