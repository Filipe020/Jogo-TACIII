"""Cenário noturno usado no jogo e no editor; funciona sem o PNG se faltar."""

import os
import pygame
from config import settings
from systems.display import sdim, spt, sval


class TempleBackground:
    def __init__(self, caminho_imagem=None, cor_fallback=None):
        caminho = caminho_imagem or getattr(
            settings,
            "COMBAT_BACKGROUND",
            os.path.join(settings.BASE_DIR, "assets", "backgrounds", "templo_noite.png"),
        )
        self.cor_fallback = cor_fallback or settings.COLOR_BG
        self.imagem = None
        if caminho and os.path.exists(caminho):
            try:
                origem = pygame.image.load(caminho).convert()
                # Uma folga horizontal permite movimento sutil de paralaxe sem lacunas.
                # Mantém o aspecto 16:9; a borda extra serve para paralaxe.
                self.imagem = pygame.transform.smoothscale(origem, sdim(1120, 630))
            except pygame.error:
                pass

    def draw(self, surface, camera_x=0):
        surface.fill(self.cor_fallback)
        if self.imagem:
            deslocamento = min(160, max(0, int(camera_x * 0.06)))
            # O trecho de pedra da arte acompanha o piso físico em y=460.
            surface.blit(self.imagem, spt(-deslocamento, -90))