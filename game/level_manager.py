"""Gerencia o nível atual e o spawner de inimigos durante a Run."""

import random

import pygame

from entities.enemy import Enemy
from config import settings
from levels.level_data import (
    BOSS_EDITOR_MARKERS,
    mapa_padrao,
    normalizar_mapa,
)


class LevelManager:
    # O encontro acontece depois de atravessar o portal no final da fase.
    # A arena substitui temporariamente o cenário normal; não há mobs misturados.
    ARENA_LARGURA = 1400
    MOBS_POR_PORTAL = 10

    def __init__(self):
        self.tempo_desde_spawn = 0.0
        self.intervalo_spawn = 2.6
        self.carregar_mapa(mapa_padrao())

    def carregar_mapa(self, dados):
        mapa = normalizar_mapa(dados)
        self.chao = pygame.Rect(0, settings.GROUND_Y, mapa["largura"],
                               settings.SCREEN_HEIGHT - settings.GROUND_Y)
        self.plataformas = [pygame.Rect(*item) for item in mapa["plataformas"]]
        self.plataformas.append(self.chao)
        self.limites = (0, mapa["largura"])
        self.spawn_jogador = tuple(mapa["spawn_jogador"])
        marcadores = [e for e in mapa["inimigos"] if e["tipo"] == "chefe"]
        self.portal_x = (int(marcadores[0]["x"]) if marcadores
                         else max(300, mapa["largura"] - 180))
        self.inimigos_iniciais = [e for e in mapa["inimigos"] if e["tipo"] != "chefe"]
        self.spawn_automatico = mapa["spawn_automatico"]
        self.chefe_posicionado = bool(marcadores)
        self.reiniciar()

    def reiniciar(self):
        self.tempo_desde_spawn = 0.0
        self.intervalo_spawn = 2.6
        self.chefe_spawnado = False
        self.chefe_concluido = False
        self.proximo_portal_mobs = self.MOBS_POR_PORTAL
        self.arena_ativa = False
        self.boss_order = ["chefe", "boss_basico", "boss_distancia", "boss_resistente", "boss_samurai"]
        self.boss_index = 0
        self._plataformas_fase = None
        self._limites_fase = None
        self._chao_fase = None

    def criar_inimigos_iniciais(self):
        inimigos = []
        for item in self.inimigos_iniciais:
            tipo_real = BOSS_EDITOR_MARKERS.get(item["tipo"], item["tipo"])
            mob = Enemy(item["x"], item["y"], tipo_real)
            if mob.y + mob.height >= settings.GROUND_Y:
                mob.y = settings.GROUND_Y - mob.height
                mob.on_ground = True
            inimigos.append(mob)
        return inimigos

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
        if not self.spawn_automatico or self.arena_ativa:
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
        enemy = Enemy(x, 0, tipo)
        enemy.y = settings.GROUND_Y - enemy.height
        enemy.on_ground = True
        return enemy

    def portal_disponivel(self, mobs_derrotados):
        return (not self.arena_ativa and not self.chefe_spawnado
                and mobs_derrotados >= self.proximo_portal_mobs)

    def portal_atingido(self, players, mobs_derrotados):
        if not self.portal_disponivel(mobs_derrotados):
            return False
        return any(p is not None and not p.morto
                   and abs(p.rect.centerx - self.portal_x) <= 52
                   for p in players)

    def entrar_arena_chefe(self):
        if self.arena_ativa or self.chefe_spawnado:
            return False
        self._plataformas_fase = self.plataformas
        self._limites_fase = self.limites
        self._chao_fase = self.chao
        self.arena_ativa = True
        self.limites = (0, self.ARENA_LARGURA)
        self.chao = pygame.Rect(0, settings.GROUND_Y, self.ARENA_LARGURA,
                               settings.SCREEN_HEIGHT - settings.GROUND_Y)
        self.plataformas = [
            self.chao,
            pygame.Rect(245, 350, 175, 22),
            pygame.Rect(985, 350, 175, 22),
        ]
        return True

    def sair_arena_chefe(self):
        if not self.arena_ativa:
            return False
        self.plataformas = self._plataformas_fase
        self.limites = self._limites_fase
        self.chao = self._chao_fase
        self._plataformas_fase = None
        self._limites_fase = None
        self._chao_fase = None
        self.arena_ativa = False
        self.chefe_concluido = True
        self.chefe_spawnado = False
        self.proximo_portal_mobs += self.MOBS_POR_PORTAL
        self.boss_index = (self.boss_index + 1) % len(self.boss_order)
        self.tempo_desde_spawn = 0.0
        return True

    def tipo_chefe_atual(self):
        return self.boss_order[self.boss_index]

    def nome_chefe_atual(self):
        nomes = {
            "chefe": "ESPECTRO ANCESTRAL",
            "boss_basico": "NECROZUMBI TITAN",
            "boss_distancia": "SENTINELA MECANICO",
            "boss_resistente": "ESPECTRO DAS CINZAS",
            "boss_samurai": "SAMURAI DO CREPUSCULO",
        }
        return nomes.get(self.tipo_chefe_atual(), "CHEFE")

    def criar_chefe(self, player_x=0):
        if not self.arena_ativa or self.chefe_spawnado:
            return None
        self.chefe_spawnado = True
        tipo = self.tipo_chefe_atual()
        prototipo = Enemy(1040, 0, tipo)
        prototipo.y = settings.GROUND_Y - prototipo.height
        prototipo.on_ground = True
        return prototipo
