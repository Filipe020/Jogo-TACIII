"""Carregador de ícones estáticos do HUD — vida, arma, pontos (GDD seção 18).

Diferente de systems/animation.py (que corta spritesheets com vários
frames), aqui cada ícone é uma única imagem PNG estática. Se o arquivo
ainda não existir, gera um placeholder simples (uma forma geométrica) pra
o HUD continuar legível enquanto a arte real não chega — basta soltar o
.png com o nome certo em assets/sprites/ui/ que ele passa a ser usado
automaticamente."""

import math
import os

import pygame


class IconLoader:
    _cache = {}

    @classmethod
    def carregar(cls, caminho, tamanho, cor_placeholder=(255, 255, 255), forma="circulo"):
        chave = (caminho, tamanho)
        if chave in cls._cache:
            return cls._cache[chave]

        if os.path.exists(caminho):
            img = pygame.image.load(caminho).convert_alpha()
            if img.get_size() != (tamanho, tamanho):
                img = pygame.transform.smoothscale(img, (tamanho, tamanho))
        else:
            img = cls._gerar_placeholder(tamanho, cor_placeholder, forma)

        cls._cache[chave] = img
        return img

    @staticmethod
    def _gerar_placeholder(tamanho, cor, forma):
        surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        centro = tamanho // 2
        raio = max(2, tamanho // 2 - 2)

        if forma == "coracao":
            r = max(2, tamanho // 4)
            pygame.draw.circle(surf, cor, (centro - r // 2, centro - r // 2 + 1), r)
            pygame.draw.circle(surf, cor, (centro + r // 2, centro - r // 2 + 1), r)
            pygame.draw.polygon(
                surf, cor,
                [(2, centro - 1), (tamanho - 2, centro - 1), (centro, tamanho - 2)],
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
                [(centro, 2), (tamanho - 2, centro), (centro, tamanho - 2), (2, centro)],
            )
        else:  # "circulo"
            pygame.draw.circle(surf, cor, (centro, centro), raio)

        pygame.draw.rect(surf, (20, 20, 20), (0, 0, tamanho, tamanho), 1, border_radius=3)
        return surf