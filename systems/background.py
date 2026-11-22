"""Cenário noturno e cenário da fase final; funciona sem o PNG se faltar."""
import os
import pygame
from config import settings


class TempleBackground:
    def __init__(self, caminho=None, cor_fundo=None):
        if caminho is None:
            caminho = getattr(
                settings,
                "COMBAT_BACKGROUND",
                os.path.join(settings.BASE_DIR, "assets", "backgrounds", "templo_noite.png"),
            )
        self.cor_fundo = cor_fundo or settings.COLOR_BG
        self.imagem = None
        if caminho and os.path.exists(caminho):
            try:
                origem = pygame.image.load(caminho).convert()
                self.imagem = pygame.transform.smoothscale(origem, (1120, 630))
            except pygame.error:
                pass

    def draw(self, surface, camera_x=0):
        surface.fill(self.cor_fundo)
        if self.imagem:
            deslocamento = min(160, max(0, int(camera_x * 0.06)))
            surface.blit(self.imagem, (-deslocamento, -45))