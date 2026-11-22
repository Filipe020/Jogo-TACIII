"""Representa um shuriken em voo — do jogador ou de um inimigo à
distância"""

import pygame

from entities.entity import Entity
from config import settings
from systems.display import spt, sval

class Projectile(Entity):
    def __init__(self, x, y, direction, speed, damage, from_player=True):
        super().__init__(x, y, 10, 10)
        self.vx = speed * direction
        self.damage = damage
        self.from_player = from_player
        self.facing = direction
        self.lifetime = 2.0  #Segundos até desaparecer sozinho
        self.rotation = 0

    def update(self, dt):
        self.x += self.vx * dt
        self.rotation = (self.rotation + 720 * dt) % 360
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface, camera_x):
        cor = settings.COLOR_SHURIKEN if self.from_player else (230, 120, 120)
        centro = spt(self.x - camera_x + self.width / 2, self.y + self.height / 2)
        raio = sval(self.width / 2)
        pygame.draw.circle(surface, cor, centro, raio)
        pygame.draw.circle(surface, (20, 20, 30), centro, raio, max(1, sval(1)))
