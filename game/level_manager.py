"""Gerencia o nível atual e o spawner de inimigos durante a Run."""

import random

import pygame

from entities.enemy import Enemy
from levels.level_data import mapa_padrao, normalizar_mapa


class LevelManager:
    def __init__(self):
        self.tempo_desde_spawn = 0.0
        self.intervalo_spawn = 2.6
        self.carregar_mapa(mapa_padrao())

    def carregar_mapa(self, dados):
        mapa = normalizar_mapa(dados)
        self.plataformas = [pygame.Rect(*item) for item in mapa["plataformas"]]
        self.limites = (0, mapa["largura"])
        self.spawn_jogador = tuple(mapa["spawn_jogador"])
        self.inimigos_iniciais = list(mapa["inimigos"])
        self.spawn_automatico = mapa["spawn_automatico"]
        self.reiniciar()

    def reiniciar(self):
        self.tempo_desde_spawn = 0.0
        self.intervalo_spawn = 2.6

    def criar_inimigos_iniciais(self):
        return [Enemy(item["x"], item["y"], item["tipo"]) for item in self.inimigos_iniciais]

    def _tipo_aleatorio(self, tempo_de_run):
        pesos = {
            "basico": 5,
            "rapido": 3,
            "resistente": max(1, min(4, int(tempo_de_run // 25))),
            "distancia": max(1, min(3, int(tempo_de_run // 20))),
        }
        tipos, peso_lista = zip(*pesos.items())
        return random.choices(tipos, weights=peso_lista, k=1)[0]

    def atualizar_spawner(self, dt, tempo_de_run, player_x, inimigos_atuais):
        if not self.spawn_automatico:
            return None
        self.tempo_desde_spawn += dt
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
        return Enemy(x, 0.0, tipo)
