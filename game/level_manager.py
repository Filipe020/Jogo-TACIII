"""Gerencia o nível atual: plataformas, limites e o spawner de inimigos durante a Run"""

import random

from levels import level_01
from entities.enemy import Enemy

class LevelManager:
    def __init__(self):
        self.plataformas = level_01.construir_plataformas()
        self.limites = level_01.limites_nivel()
        self.spawn_jogador = level_01.spawn_inicial_jogador()

        self.tempo_desde_spawn = 0.0
        self.intervalo_spawn = 2.6

    def reiniciar(self):
        self.tempo_desde_spawn = 0.0
        self.intervalo_spawn = 2.6

    def _tipo_aleatorio(self, tempo_de_run):
        #Quanto mais tempo de Run, maior a chance de inimigos mais difíceis.
        pesos = {
            "basico": 5,
            "rapido": 3,
            "resistente": max(1, min(4, int(tempo_de_run // 25))),
            "distancia": max(1, min(3, int(tempo_de_run // 20))),
        }
        tipos, peso_lista = zip(*pesos.items())
        return random.choices(tipos, weights=peso_lista, k=1)[0]

    def atualizar_spawner(self, dt, tempo_de_run, player_x, inimigos_atuais):
        self.tempo_desde_spawn += dt

        #A cada 20s de Run, o spawn fica um pouco mais frequente (mín. 0.9s).
        self.intervalo_spawn = max(0.9, 2.6 - (tempo_de_run // 20) * 0.15)

        if self.tempo_desde_spawn >= self.intervalo_spawn and len(inimigos_atuais) < 10:
            self.tempo_desde_spawn = 0.0
            return self._spawnar_inimigo(tempo_de_run, player_x)
        return None

    def _spawnar_inimigo(self, tempo_de_run, player_x):
        tipo = self._tipo_aleatorio(tempo_de_run)
        lado = random.choice([-1, 1])
        distancia = random.randint(420, 700)
        x = max(self.limites[0], min(self.limites[1] - 40, player_x + lado * distancia))
        y = 0.0  # cai de cima; a física/colisão resolve o pouso na plataforma
        return Enemy(x, y, tipo)
