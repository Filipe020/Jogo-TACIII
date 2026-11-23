"""Classe base para as armas do jogador."""

class Weapon:
    def __init__(self, dano_base, alcance, cooldown):
        self.dano_base = dano_base
        self.alcance = alcance
        self.cooldown = cooldown
        self.tempo_desde_ultimo_ataque = cooldown  #já pode atacar de início

    def pode_atacar(self):
        return self.tempo_desde_ultimo_ataque >= self.cooldown

    def resetar_cooldown(self):
        self.tempo_desde_ultimo_ataque = 0.0

    def atualizar(self, dt):
        self.tempo_desde_ultimo_ataque += dt