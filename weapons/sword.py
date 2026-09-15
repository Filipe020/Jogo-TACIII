"""Espada: alto dano, alcance curto, ataque rápido (GDD seção 8.1)."""

import pygame

from weapons.weapon import Weapon
from systems.combat import calculate_damage


class Sword(Weapon):
    def __init__(self, dano_base=18, alcance=40, cooldown=0.28):
        super().__init__(dano_base, alcance, cooldown)
        self.altura = 34

    def calcular_dano(self, multiplicador=1.0):
        return calculate_damage(self.dano_base, multiplicador)

    def hitbox(self, player):
        """Retângulo de ataque na frente do jogador, conforme a direção
        que ele está olhando."""
        if player.facing > 0:
            x = player.rect.right
        else:
            x = player.rect.left - self.alcance
        y = player.rect.centery - self.altura // 2
        return pygame.Rect(int(x), int(y), self.alcance, self.altura)
