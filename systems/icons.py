"""Carregador de ícones estáticos do HUD — vida, arma, pontos (GDD seção 18)."""

import math
import os

import pygame
from systems.display import sval


class IconLoader:
    _cache = {}

    @classmethod
    def carregar(cls, caminho, tamanho, cor_placeholder=(255, 255, 255), forma="circulo"):
        tamanho_px = sval(tamanho)
        chave = (caminho, tamanho_px)
        if chave in cls._cache:
            return cls._cache[chave]

        if os.path.exists(caminho):
            img = pygame.image.load(caminho).convert_alpha()
            if img.get_size() != (tamanho_px, tamanho_px):
                img = pygame.transform.smoothscale(img, (tamanho_px, tamanho_px))
        else:
            img = cls._gerar_placeholder(tamanho_px, cor_placeholder, forma)

        cls._cache[chave] = img
        return img

    @staticmethod
    def _gerar_placeholder(tamanho, cor, forma):
        surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        centro = tamanho // 2
        raio = max(2, tamanho // 2 - sval(2))
        b = max(1, sval(2))

        if forma == "coracao":
            r = max(2, tamanho // 4)
            pygame.draw.circle(surf, cor, (centro - r // 2, centro - r // 2 + sval(1)), r)
            pygame.draw.circle(surf, cor, (centro + r // 2, centro - r // 2 + sval(1)), r)
            pygame.draw.polygon(
                surf, cor,
                [(b, centro - sval(1)), (tamanho - b, centro - sval(1)), (centro, tamanho - b)],
            )
        elif forma == "estrela":
            pontos = []
            for i in range(10):
                ang = math.pi / 2 + i * math.pi / 5
                r = raio if i % 2 == 0 else raio // 2
                pontos.append((centro + r * math.cos(ang), centro - r * math.sin(ang)))
            pygame.draw.polygon(surf, cor, pontos)
        elif forma == "diamante":
            pygame.draw.polygon(
                surf, cor,
                [(centro, b), (tamanho - b, centro), (centro, tamanho - b), (b, centro)],
            )
        else:
            pygame.draw.circle(surf, cor, (centro, centro), raio)

        pygame.draw.rect(surf, (20, 20, 20), (0, 0, tamanho, tamanho), max(1, sval(1)), border_radius=sval(3))
        return surf
