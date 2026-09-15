"""Shuriken: ataque à distância, dano menor que a espada, quantidade
controlada pelo sistema do jogo (GDD seção 8.2)."""

from weapons.weapon import Weapon
from systems.combat import calculate_damage


class ShurikenWeapon(Weapon):
    def __init__(self, dano_base=9, cooldown=0.45):
        super().__init__(dano_base, alcance=9999, cooldown=cooldown)

    def calcular_dano(self, multiplicador=1.0):
        return calculate_damage(self.dano_base, multiplicador)
