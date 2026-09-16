"""Controla o estado geral do jogo: menu, Run, pausa, morte e Sala de Evolução"""

import pygame

from game.game_state import GameState, RunState
from game.level_manager import LevelManager
from entities.player import Player
from systems.progression import Progression
from systems.collision import check_attack_hit
from systems.audio import AudioManager
from ui.main_menu import MainMenu
from ui.hud import HUD
from ui.evolution_menu import EvolutionMenu
from ui.game_over import GameOverScreen
from config import settings

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.MENU

        self.progression = Progression()
        self.run_state = RunState()
        self.level_manager = LevelManager()
        self.audio = AudioManager()

        self.player = None
        self.enemies = []
        self.camera_x = 0.0

        self.main_menu = MainMenu()
        self.hud = HUD()
        self.evolution_menu = EvolutionMenu(self.progression)
        self.game_over_screen = GameOverScreen()

        self.game_over_timer = 0.0

    #---Transições de estado---
    def iniciar_run(self):
        self.run_state.reiniciar()
        self.level_manager.reiniciar()
        spawn_x, spawn_y = self.level_manager.spawn_jogador
        self.player = Player(spawn_x, spawn_y, self.progression)
        self.enemies = []
        self.camera_x = 0.0
        self.state = GameState.RUN

    def encerrar_run(self):
        self.progression.encerrar_run(self.run_state)
        self.state = GameState.GAME_OVER
        self.game_over_timer = 1.4

    def entrar_sala_evolucao(self):
        self.evolution_menu.atualizar_opcoes()
        self.state = GameState.SALA_EVOLUCAO

    #---Eventos---
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            if self.state == GameState.RUN:
                self.state = GameState.PAUSADO
            elif self.state == GameState.PAUSADO:
                self.state = GameState.RUN

        if self.state == GameState.MENU and event.key == pygame.K_RETURN:
            self.iniciar_run()
            self.audio.play("menu")

        elif self.state == GameState.SALA_EVOLUCAO:
            self.evolution_menu.handle_event(event, self.audio)
            if self.evolution_menu.confirmar_iniciar_run:
                self.evolution_menu.confirmar_iniciar_run = False
                self.iniciar_run()

    #---Atualização---
    def update(self, dt):
        keys = pygame.key.get_pressed()

        if self.state == GameState.RUN:
            self._atualizar_run(dt, keys)
        elif self.state == GameState.GAME_OVER:
            self.game_over_timer -= dt
            if self.game_over_timer <= 0:
                self.entrar_sala_evolucao()

    def _atualizar_run(self, dt, keys):
        self.run_state.tempo_de_run += dt

        self.player.handle_input(keys, self.audio)
        self.player.update(dt, self.level_manager.plataformas, self.level_manager.limites)

        novo_inimigo = self.level_manager.atualizar_spawner(
            dt, self.run_state.tempo_de_run, self.player.x, self.enemies
        )
        if novo_inimigo:
            self.enemies.append(novo_inimigo)

        for inimigo in self.enemies:
            inimigo.atualizar_ia(dt, self.player, self.level_manager.plataformas, self.level_manager.limites)

        self._resolver_combate()
        #Mantém o inimigo na cena até a animação de morte terminar de tocar.
        self.enemies = [e for e in self.enemies if not e.animacao_morte_terminou()]

        #Câmera segue o jogador horizontalmente
        alvo_camera = self.player.rect.centerx - settings.SCREEN_WIDTH // 2
        alvo_camera = max(
            self.level_manager.limites[0],
            min(alvo_camera, self.level_manager.limites[1] - settings.SCREEN_WIDTH),
        )
        self.camera_x += (alvo_camera - self.camera_x) * min(1, dt * 6)

        if self.player.morto:
            self.encerrar_run()

    def _resolver_combate(self):
        #Espada do jogador x inimigos
        hitbox = self.player.sword_hitbox()
        if hitbox:
            atingidos = check_attack_hit(hitbox, self.enemies)
            for inimigo in atingidos:
                if not inimigo.alive:
                    continue
                inimigo.receber_dano(self.player._dano_espada(), self.audio)
                if not inimigo.alive:
                    self.progression.registrar_kill_run(self.run_state)

        #Shurikens do jogador x inimigos
        for proj in self.player.projectiles:
            if not proj.alive:
                continue
            for inimigo in self.enemies:
                if inimigo.alive and proj.rect.colliderect(inimigo.rect):
                    inimigo.receber_dano(proj.damage, self.audio)
                    proj.alive = False
                    if not inimigo.alive:
                        self.progression.registrar_kill_run(self.run_state)
                    break

        #Projéteis de inimigos à distância x jogador
        for inimigo in self.enemies:
            for proj in inimigo.projectiles:
                if proj.alive and proj.rect.colliderect(self.player.rect):
                    self.player.receber_dano(proj.damage, self.audio)
                    proj.alive = False

    #---Desenho---
    def draw(self):
        if self.state == GameState.MENU:
            self.main_menu.draw(self.screen)
        elif self.state in (GameState.RUN, GameState.PAUSADO):
            self._desenhar_run()
            if self.state == GameState.PAUSADO:
                self._desenhar_pausa()
        elif self.state == GameState.GAME_OVER:
            self._desenhar_run()
            self.game_over_screen.draw(self.screen, self.run_state)
        elif self.state == GameState.SALA_EVOLUCAO:
            self.evolution_menu.draw(self.screen, self.progression, self.run_state)

    def _desenhar_run(self):
        self.screen.fill(settings.COLOR_BG)
        cam = int(self.camera_x)

        for plat in self.level_manager.plataformas:
            r = plat.copy()
            r.x -= cam
            pygame.draw.rect(self.screen, settings.COLOR_PLATFORM, r)
            pygame.draw.rect(self.screen, settings.COLOR_PLATFORM_TOP, (r.x, r.y, r.width, 6))

        for inimigo in self.enemies:
            inimigo.draw(self.screen, cam)

        self.player.draw(self.screen, cam)
        self.hud.draw(self.screen, self.player, self.run_state)

    def _desenhar_pausa(self):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        fonte = pygame.font.SysFont("consolas", 36, bold=True)
        texto = fonte.render("PAUSADO", True, settings.COLOR_TEXT)
        self.screen.blit(texto, texto.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)))

        fonte2 = pygame.font.SysFont("consolas", 18)
        texto2 = fonte2.render("ESC para continuar", True, settings.COLOR_TEXT)
        self.screen.blit(
            texto2, texto2.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 40))
        )
