"""Classe base para objetos com posição, tamanho e retângulo de colisão
(GDD seção 30 - Principais Classes)."""

import pygame


class Entity:
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.facing = 1  # 1 = direita, -1 = esquerda
        self.on_ground = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, dt):
        pass

    def draw(self, surface, camera_x):
        pass
