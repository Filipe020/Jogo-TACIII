"""Controla o estado geral do jogo: menu, Run, pausa, morte e Sala de Evolução"""

import os
import random
import pygame

from game.game_state import GameState, RunState
from game.level_manager import LevelManager
from entities.player import Player
from entities.enemy import Enemy
from entities.projectile import Projectile
from network.lan import LANPeer, PORT, local_ip
from levels.level_data import normalizar_mapa, carregar_slot, mapa_padrao
from systems.progression import Progression, UPGRADE_DEFS
from systems.collision import check_attack_hit
from systems.audio import AudioManager
from ui.main_menu import MainMenu
from ui.hud import HUD
from ui.evolution_menu import EvolutionMenu
from ui.upgrade_menu import UpgradeMenu
from ui.game_over import GameOverScreen
from ui.level_editor import LevelEditor
from systems.background import TempleBackground
from systems.display import font, mouse_pos, sdim, spt, srect, sval
from config import settings


class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.MENU

        self.progression = Progression()
        self.run_progression = self.progression
        self.run_state = RunState()
        self.level_manager = LevelManager()
        self.audio = AudioManager()

        self.player = None
        self.enemies = []
        self.camera_x = 0.0

        self.background = TempleBackground()
        self.boss_background = TempleBackground(settings.BOSS_BACKGROUND, settings.COLOR_BOSS_BG)
        self.editor = LevelEditor(self.background)
        self.em_teste = False

        self.main_menu = MainMenu()
        self.hud = HUD()
        self.evolution_menu = EvolutionMenu(self.progression)
        self.upgrade_menu = UpgradeMenu()
        self.game_over_screen = GameOverScreen()
        self.sair_solicitado = False

        self.game_over_timer = 0.0
        self.lan = None
        self.lan_role = None
        self.multiplayer = False
        self.remote_player = None
        self.remote_actions = {}
        self.remote_input_age = 0.0
        self.net_timer = 0.0
        self.client_enemies = {}
        self.lan_message = ""
        self.pausa_selecionado = 0

        self.fullscreen = bool(getattr(settings, "FULLSCREEN", True))

        self.meta_inimigos = settings.INIMIGOS_PARA_CHEFE
        self.terremoto_timer = 0.0
        self.terremoto_ativado = False
        self.aviso_chefe_timer = 0.0
        self.porta_rect = None

    
    
    def alternar_tela_cheia(self):
        self.fullscreen = not getattr(self, "fullscreen", bool(getattr(settings, "FULLSCREEN", True)))
        settings.FULLSCREEN = self.fullscreen
        flags = (pygame.FULLSCREEN | pygame.SCALED) if self.fullscreen else pygame.SCALED
        try:
            self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), flags)
        except pygame.error:
            fallback_flags = pygame.FULLSCREEN if self.fullscreen else 0
            self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), fallback_flags)
    

    def _ativar_evento_chefe(self):
        if self.terremoto_ativado or self.run_state.fase_atual != 1:
            return
        self.terremoto_ativado = True
        self.terremoto_timer = settings.DURACAO_TERREMOTO
        self.aviso_chefe_timer = 5.5
        self.run_state.porta_liberada = True
        self.audio.play("player_death")

        # Cria a porta sobre o chão próximo ao jogador
        porta_w, porta_h = 56, 86
        px = max(80, min(self.level_manager.limites[1] - 140, int(self.player.rect.centerx + 110)))
        chao_y = 460
        for plat in self.level_manager.plataformas:
            if plat.left <= px <= plat.right and plat.top >= self.player.rect.bottom - 10:
                chao_y = plat.top
                break
        self.porta_rect = pygame.Rect(px, chao_y - porta_h, porta_w, porta_h)

    def avancar_fase_final(self):
        from levels.boss_arena import mapa_fase_final
        mapa = normalizar_mapa(mapa_fase_final())
        self.level_manager.carregar_mapa(mapa)
        self.run_state.fase_atual = 2
        self.run_state.porta_liberada = False
        self.porta_rect = None
        self.enemies = []
        spawn_x, spawn_y = self.level_manager.spawn_jogador
        self.player.x, self.player.y = float(spawn_x), float(spawn_y)
        self.player.vx = self.player.vy = 0.0
        self.player.projectiles.clear()
        if self.multiplayer and self.remote_player:
            self.remote_player.x, self.remote_player.y = float(spawn_x + 68), float(spawn_y)
            self.remote_player.vx = self.remote_player.vy = 0.0
            self.remote_player.projectiles.clear()
        self.camera_x = 0.0
        self.audio.play("upgrade")

    #---Transições de estado---
    def iniciar_run(self, mapa=None, teste=False, multiplayer=False):
        """ENTER usa o slot salvo; F5 usa inclusive alterações ainda não salvas."""
        if mapa is None:
            try:
                mapa = carregar_slot(self.editor.slot) or mapa_padrao()
            except Exception:
                mapa = mapa_padrao()
        try:
            mapa = normalizar_mapa(mapa)
        except Exception:
            mapa = normalizar_mapa(mapa_padrao())
        self.level_manager.carregar_mapa(mapa)

        self.meta_inimigos = settings.INIMIGOS_PARA_CHEFE
        self.run_state.reiniciar(meta_inimigos=self.meta_inimigos)
        self.terremoto_timer = 0.0
        self.terremoto_ativado = False
        self.aviso_chefe_timer = 0.0
        self.porta_rect = None

        self.multiplayer = multiplayer
        # Testes do editor e LAN não modificam o save solo do jogador.
        self.run_progression = (
            Progression(carregar=False, persistir=False)
            if teste or multiplayer
            else self.progression
        )
        spawn_x, spawn_y = self.level_manager.spawn_jogador
        self.player = Player(
            spawn_x + (68 if multiplayer and self.lan_role == "client" else 0),
            spawn_y,
            self.run_progression,
        )
        self.remote_player = None
        if multiplayer:
            self.remote_player = Player(
                spawn_x + (0 if self.lan_role == "client" else 68),
                spawn_y,
                self.run_progression,
            )
        self.client_enemies = {}
        self.enemies = self.level_manager.criar_inimigos_iniciais(limite_total=self.run_state.meta_inimigos)
        self.run_state.inimigos_spawnados = len(self.enemies)
        self.camera_x = 0.0
        self.em_teste = teste
        self.pausa_selecionado = 0
        self.upgrade_menu.abrir()
        self.state = GameState.RUN

    def encerrar_run(self):
        self.run_progression.encerrar_run(self.run_state)
        self.state = GameState.GAME_OVER
        self.game_over_timer = 1.4

    def entrar_sala_evolucao(self):
        self.evolution_menu.atualizar_opcoes()
        self.state = GameState.SALA_EVOLUCAO

    #---Multiplayer LAN---
    def _voltar_menu_lan(self, mensagem=""):
        if self.lan is not None:
            self.lan.close()
        self.lan = None
        self.lan_role = None
        self.multiplayer = False
        self.remote_player = None
        self.remote_actions = {}
        self.state = GameState.MENU
        self.main_menu.tela = "multiplayer" if mensagem else "principal"
        if mensagem:
            self.main_menu.avisar(mensagem)

    def _iniciar_lan(self, role, address=""):
        self._voltar_menu_lan()
        if role == "client" and not address.strip():
            self.main_menu.tela = "multiplayer"
            self.main_menu.avisar("Digite o IP do anfitrião.")
            return
        self.lan_role = role
        self.lan = LANPeer(role, address.strip(), PORT)
        self.lan_message = (
            f"Sala criada! IP: {local_ip()}  Porta: {PORT}"
            if role == "host"
            else f"Conectando a {address}:{PORT}..."
        )
        self.remote_actions = {}
        self.remote_input_age = 0.0
        self.net_timer = 0.0
        self.state = GameState.LAN_LOBBY

    def _processar_lan(self, dt):
        if self.lan is None:
            return
        if self.lan.status in ("erro", "desconectado", "fechado"):
            motivo = self.lan.error or "Jogador desconectado."
            self._voltar_menu_lan("LAN: " + motivo[:65])
            return
        if self.lan_role == "host" and self.lan.status == "conectado" and self.state == GameState.LAN_LOBBY:
            try:
                mapa = carregar_slot(self.editor.slot) or mapa_padrao()
                mapa = normalizar_mapa(mapa)
            except (OSError, ValueError, KeyError, TypeError):
                mapa = mapa_padrao()
            self.iniciar_run(mapa=mapa, multiplayer=True)
            self.lan.send({"type": "welcome", "map": mapa})

        for message in self.lan.receive():
            tipo = message.get("type")
            if self.lan_role == "host" and tipo == "input":
                actions = message.get("actions", {})
                if isinstance(actions, dict):
                    self.remote_actions = {
                        key: bool(actions.get(key)) for key in ("left", "right", "jump", "sword", "shuriken")
                    }
                    self.remote_input_age = 0.0
            elif self.lan_role == "host" and tipo == "upgrade":
                chave = message.get("key")
                if self.multiplayer and self.state in (GameState.RUN, GameState.PAUSADO, GameState.HABILIDADES):
                    if isinstance(chave, str) and chave in UPGRADE_DEFS:
                        self._comprar_habilidade(chave)
            elif self.lan_role == "client" and tipo == "welcome" and self.state == GameState.LAN_LOBBY:
                try:
                    self.iniciar_run(mapa=message["map"], multiplayer=True)
                except (ValueError, KeyError, TypeError):
                    self._voltar_menu_lan("Mapa recebido é inválido.")
                    return
            elif self.lan_role == "client" and tipo == "snapshot" and self.state in (GameState.RUN, GameState.PAUSADO, GameState.HABILIDADES):
                try:
                    self._aplicar_snapshot(message)
                except (ValueError, KeyError, TypeError, IndexError):
                    continue

        if self.state not in (GameState.RUN, GameState.PAUSADO, GameState.HABILIDADES) or not self.multiplayer:
            return
        self.net_timer += dt
        if self.lan_role == "host":
            self.remote_input_age += dt
            if self.remote_input_age > 0.4:
                self.remote_actions = {}
            if self.net_timer >= 1 / 20:
                self.net_timer = 0.0
                self.lan.send(self._criar_snapshot())
        elif self.net_timer >= 1 / 30:
            self.net_timer = 0.0
            keys = pygame.key.get_pressed()
            buttons = pygame.mouse.get_pressed()
            self.lan.send({
                "type": "input",
                "actions": {
                    "left": self.state == GameState.RUN and bool(keys[pygame.K_a]),
                    "right": self.state == GameState.RUN and bool(keys[pygame.K_d]),
                    "jump": self.state == GameState.RUN and bool(keys[pygame.K_w] or keys[pygame.K_SPACE]),
                    "sword": self.state == GameState.RUN and bool(buttons[0]),
                    "shuriken": self.state == GameState.RUN and bool(buttons[2]),
                },
            })

    @staticmethod
    def _dados_proj(proj):
        return [round(proj.x, 2), round(proj.y, 2), int(proj.facing)]

    @staticmethod
    def _dados_player(player):
        return {
            "x": round(player.x, 2),
            "y": round(player.y, 2),
            "vx": round(player.vx, 2),
            "vy": round(player.vy, 2),
            "facing": player.facing,
            "health": player.health,
            "max_health": player.max_health,
            "shurikens": player.shurikens,
            "shurikens_max": player.shurikens_max,
            "morto": player.morto,
            "invulneravel": round(player.invulneravel_timer, 2),
            "anim": player.anim.estado_atual,
            "attack": round(player.ataque_visual_timer, 2),
            "projectiles": [GameManager._dados_proj(proj) for proj in player.projectiles if proj.alive],
        }

    def _criar_snapshot(self):
        return {
            "type": "snapshot",
            "kills": self.run_state.inimigos_derrotados,
            "upgrades": self.run_progression.estado_rede(),
            "players": [self._dados_player(self.player), self._dados_player(self.remote_player)],
            "enemies": [
                {
                    "id": e.uid,
                    "tipo": e.tipo,
                    "x": round(e.x, 2),
                    "y": round(e.y, 2),
                    "facing": e.facing,
                    "health": e.health,
                    "alive": e.alive,
                    "anim": e.anim.estado_atual,
                    "projectiles": [self._dados_proj(p) for p in e.projectiles if p.alive],
                }
                for e in self.enemies
            ],
        }

    @staticmethod
    def _restaurar_proj(items, from_player):
        projeteis = []
        for x, y, facing in items[:40]:
            p = Projectile(x, y, facing, 0, 0, from_player=from_player)
            projeteis.append(p)
        return projeteis

    def _aplicar_player(self, player, dados):
        player.x = float(dados["x"])
        player.y = float(dados["y"])
        player.vx = float(dados["vx"])
        player.vy = float(dados["vy"])
        player.facing = int(dados["facing"])
        player.health = float(dados["health"])
        player.max_health = float(dados["max_health"])
        player.shurikens = int(dados["shurikens"])
        player.shurikens_max = int(dados["shurikens_max"])
        player.morto = bool(dados["morto"])
        player.invulneravel_timer = float(dados["invulneravel"])
        player.ataque_visual_timer = float(dados["attack"])
        player.anim.trocar_estado(dados["anim"])
        player.projectiles = self._restaurar_proj(dados["projectiles"], True)

    def _aplicar_snapshot(self, dados):
        self._aplicar_player(self.remote_player, dados["players"][0])
        self._aplicar_player(self.player, dados["players"][1])
        self.run_state.inimigos_derrotados = int(dados["kills"])
        self.run_progression.receber_estado_remoto(dados.get("upgrades"))
        self._aplicar_melhorias_jogadores()
        vivos = {}
        for item in dados["enemies"][:200]:
            uid = int(item["id"])
            e = self.client_enemies.get(uid)
            if e is None:
                e = Enemy(item["x"], item["y"], item["tipo"])
            e.x = float(item["x"])
            e.y = float(item["y"])
            e.facing = int(item["facing"])
            e.health = float(item["health"])
            e.alive = bool(item["alive"])
            e.anim.trocar_estado(item["anim"])
            e.projectiles = self._restaurar_proj(item["projectiles"], False)
            vivos[uid] = e
        self.client_enemies = vivos
        self.enemies = list(vivos.values())

    def _atualizar_cliente(self, dt):
        if self.player is None:
            return
        self.player.anim.atualizar(dt)
        self.remote_player.anim.atualizar(dt)
        for enemy in self.enemies:
            enemy.anim.atualizar(dt)
        self._atualizar_camera(dt)

    def _atualizar_camera(self, dt):
        alvo = self.player.rect.centerx - settings.SCREEN_WIDTH // 2
        alvo = max(self.level_manager.limites[0], min(alvo, self.level_manager.limites[1] - settings.SCREEN_WIDTH))
        self.camera_x += (alvo - self.camera_x) * min(1, dt * 6)

    #---Evolução durante a partida---
    def _aplicar_melhorias_jogadores(self):
        for jogador in (self.player, self.remote_player):
            if jogador is not None:
                jogador.aplicar_melhorias()

    def _comprar_habilidade(self, chave):
        if chave not in UPGRADE_DEFS or not self.run_progression.pode_comprar(chave):
            self.upgrade_menu.avisar("Pontos insuficientes ou nível máximo alcançado.")
            return False
        if self.multiplayer and self.lan_role == "client":
            # Cliente só solicita; o anfitrião valida e aplica a compra.
            if self.lan is not None:
                self.lan.send({"type": "upgrade", "key": chave})
                self.upgrade_menu.avisar("Compra enviada ao anfitrião...")
                return True
            return False
        if self.run_progression.comprar(chave):
            self._aplicar_melhorias_jogadores()
            self.audio.play("upgrade")
            self.upgrade_menu.avisar("Habilidade evoluída com sucesso!")
            return True
        return False

    def _abrir_habilidades(self):
        self.upgrade_menu.abrir()
        self.state = GameState.HABILIDADES

    #---Menu de pausa---
    def _opcoes_pausa(self):
        opcoes = [("continuar", "CONTINUAR")]
        if self.em_teste:
            opcoes.append(("editor", "VOLTAR AO EDITOR"))
        opcoes.append(("menu", "VOLTAR AO MENU"))
        largura = 330
        altura = 48
        espacamento = 13
        inicio = settings.SCREEN_HEIGHT // 2 - 35
        return [
            (
                acao,
                rotulo,
                pygame.Rect(
                    (settings.SCREEN_WIDTH - largura) // 2,
                    inicio + i * (altura + espacamento),
                    largura,
                    altura,
                ),
            )
            for i, (acao, rotulo) in enumerate(opcoes)
        ]

    def _abrir_pausa(self):
        self.pausa_selecionado = 0
        self.state = GameState.PAUSADO

    def _executar_opcao_pausa(self, acao):
        if acao == "continuar":
            self.state = GameState.RUN
        elif acao == "editor" and self.em_teste:
            self.state = GameState.EDITOR
            self.em_teste = False
            self.editor.informar("Teste encerrado. Ajuste sua fase ou Ctrl+S para salvar.")
        elif acao == "menu":
            if self.multiplayer:
                self._voltar_menu_lan()
                self.main_menu.avisar("Voce saiu da partida LAN.")
            else:
                self.state = GameState.MENU
                self.main_menu.tela = "principal"
            self.em_teste = False

    #---Eventos---
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            self.alternar_tela_cheia()
            return
        if self.state == GameState.EDITOR:
            acao = self.editor.handle_event(event)
            if acao == "menu":
                self.state = GameState.MENU
            elif acao == "testar":
                self.iniciar_run(mapa=self.editor.mapa, teste=True)
            return

        if self.state == GameState.MENU:
            tem_save = os.path.exists(settings.SAVE_FILE)
            acao = self.main_menu.handle_event(event, tem_save)
            if acao == "lan_host":
                self._iniciar_lan("host")
            elif acao and acao.startswith("lan_join:"):
                self._iniciar_lan("client", acao.partition(":")[2])
            elif acao == "editor":
                self.state = GameState.EDITOR
                self.editor.informar("Bem-vindo ao editor. F5 testa a fase atual.")
            elif acao == "novo_jogo":
                # Diferente de Continuar, Novo Jogo nunca herda níveis anteriores.
                self.progression.reiniciar_novo_jogo()
                self.iniciar_run(mapa=mapa_padrao())
                self.audio.play("menu")
            elif acao == "continuar":
                self.iniciar_run()
                self.audio.play("menu")
                return
            elif acao == "toggle_fullscreen":
                self.alternar_tela_cheia()
                self.audio.play("menu")
            elif acao == "sair":
                self.sair_solicitado = True
                return

        if self.state == GameState.HABILIDADES:
            acao = self.upgrade_menu.handle_event(event)
            if acao == "fechar":
                self.state = GameState.RUN
            elif acao is not None:
                self._comprar_habilidade(acao)
            return

        if self.state == GameState.LAN_LOBBY:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._voltar_menu_lan()
            return

        if self.state == GameState.PAUSADO:
            opcoes = self._opcoes_pausa()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (acao, _, rect) in enumerate(opcoes):
                    if rect.collidepoint(event.pos):
                        self.pausa_selecionado = i
                        self._executar_opcao_pausa(acao)
                        return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._executar_opcao_pausa("continuar")
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.pausa_selecionado = (self.pausa_selecionado - 1) % len(opcoes)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.pausa_selecionado = (self.pausa_selecionado + 1) % len(opcoes)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._executar_opcao_pausa(opcoes[self.pausa_selecionado][0])
            return

        if self.state == GameState.RUN:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.upgrade_menu.HUD_RECT.collidepoint(event.pos):
                    self._abrir_habilidades()
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                self._abrir_habilidades()
                return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE and self.state == GameState.RUN:
            self._abrir_pausa()
            return

        if self.state == GameState.SALA_EVOLUCAO:
            self.evolution_menu.handle_event(event, self.audio)
            if self.evolution_menu.confirmar_iniciar_run:
                self.evolution_menu.confirmar_iniciar_run = False
                self.iniciar_run()

    #---Atualização---
    def update(self, dt):
        self._processar_lan(dt)
        keys = pygame.key.get_pressed()

        if self.state == GameState.MENU:
            self.main_menu.update(dt)
        elif self.state == GameState.RUN:
            if self.multiplayer and self.lan_role == "client":
                self._atualizar_cliente(dt)
            else:
                self._atualizar_run(dt, keys)
        elif self.state == GameState.HABILIDADES:
            self.upgrade_menu.update(dt)
            if self.multiplayer:
                # Em LAN, não interrompe a simulação do outro computador.
                if self.lan_role == "client":
                    self._atualizar_cliente(dt)
                else:
                    self._atualizar_run(dt, keys, paused_local=True)
        elif self.state == GameState.PAUSADO and self.multiplayer:
            if self.lan_role == "client":
                self._atualizar_cliente(dt)
            else:
                self._atualizar_run(dt, keys, paused_local=True)
        elif self.state == GameState.EDITOR:
            self.editor.update(dt)
        elif self.state == GameState.GAME_OVER:
            self.game_over_timer -= dt
            if self.game_over_timer <= 0:
                self.entrar_sala_evolucao()

    def _atualizar_run(self, dt, keys, paused_local=False):
        if self.aviso_chefe_timer > 0:
            self.aviso_chefe_timer = max(0.0, self.aviso_chefe_timer - dt)

        # Trava a jogabilidade enquanto o terremoto acontece e exibe "O CHEFE ESTÁ AGUARDANDO"
        if self.terremoto_timer > 0:
            self.terremoto_timer = max(0.0, self.terremoto_timer - dt)
            self.player.vx = 0
            self.player.anim.atualizar(dt)
            return

        self.run_state.tempo_de_run += dt

        if paused_local:
            self.player.handle_actions({}, self.audio)
        else:
            self.player.handle_input(keys, self.audio)
        self.player.update(dt, self.level_manager.plataformas, self.level_manager.limites)
        if self.multiplayer and self.remote_player:
            self.remote_player.handle_actions(self.remote_actions, self.audio)
            self.remote_player.update(dt, self.level_manager.plataformas, self.level_manager.limites)

        if self.run_state.fase_atual == 1:
            novo_inimigo = self.level_manager.atualizar_spawner(
                dt,
                self.run_state.tempo_de_run,
                self.player.x,
                self.enemies,
                total_spawnados=self.run_state.inimigos_spawnados,
                limite_total=self.run_state.meta_inimigos,
            )
            if novo_inimigo:
                self.enemies.append(novo_inimigo)
                self.run_state.inimigos_spawnados += 1

        for inimigo in self.enemies:
            alvos = [p for p in (self.player, self.remote_player) if p is not None and not p.morto]
            if alvos:
                alvo = min(
                    alvos,
                    key=lambda p: abs(p.rect.centerx - inimigo.rect.centerx)
                    + abs(p.rect.centery - inimigo.rect.centery),
                )
                inimigo.atualizar_ia(dt, alvo, self.level_manager.plataformas, self.level_manager.limites)

        self._resolver_combate()
        # Mantém o inimigo na cena até a animação de morte terminar de tocar.
        self.enemies = [e for e in self.enemies if not e.animacao_morte_terminou()]

        if (
            self.run_state.fase_atual == 1
            and not self.terremoto_ativado
            and self.run_state.inimigos_derrotados >= self.run_state.meta_inimigos
        ):
            self._ativar_evento_chefe()

        # Entrar na porta pressionando E ou ENTER
        if self.porta_rect and not paused_local:
            jogadores = [p for p in (self.player, self.remote_player) if p is not None and not p.morto]
            na_porta = any(j.rect.colliderect(self.porta_rect.inflate(16, 16)) for j in jogadores)
            if na_porta and (keys[pygame.K_e] or keys[pygame.K_RETURN]):
                self.avancar_fase_final()
                return

        self._atualizar_camera(dt)

        if self.player.morto and self.multiplayer:
            if self.remote_player and self.remote_player.morto:
                self._voltar_menu_lan("Os dois ninjas caíram! Partida encerrada.")
        elif self.player.morto:
            if self.em_teste:
                self.state = GameState.EDITOR
                self.editor.informar("Jogador morreu no teste. F5 para tentar novamente.")
            else:
                self.encerrar_run()

    def _resolver_combate(self):
        jogadores = [p for p in (self.player, self.remote_player) if p is not None]
        for jogador in jogadores:
            if jogador.morto:
                continue
            hitbox = jogador.sword_hitbox()
            if hitbox:
                for inimigo in check_attack_hit(hitbox, self.enemies):
                    if inimigo.alive and inimigo.uid not in jogador.atingidos_espada:
                        jogador.atingidos_espada.add(inimigo.uid)
                        inimigo.receber_dano(jogador._dano_espada(), self.audio)
                        if not inimigo.alive:
                            self.run_progression.registrar_kill_run(self.run_state)
            for proj in jogador.projectiles:
                if not proj.alive:
                    continue
                for inimigo in self.enemies:
                    if inimigo.alive and proj.rect.colliderect(inimigo.rect):
                        inimigo.receber_dano(proj.damage, self.audio)
                        proj.alive = False
                        if not inimigo.alive:
                            self.run_progression.registrar_kill_run(self.run_state)
                        break

        for inimigo in self.enemies:
            for proj in inimigo.projectiles:
                if not proj.alive:
                    continue
                for jogador in jogadores:
                    if not jogador.morto and proj.rect.colliderect(jogador.rect):
                        jogador.receber_dano(proj.damage, self.audio)
                        proj.alive = False
                        break

    #---Desenho---
    def draw(self):
        if self.state == GameState.MENU:
            self.main_menu.draw(self.screen, os.path.exists(settings.SAVE_FILE))
        elif self.state == GameState.EDITOR:
            self.editor.draw(self.screen)
        elif self.state == GameState.LAN_LOBBY:
            self._desenhar_lobby()
        elif self.state in (GameState.RUN, GameState.PAUSADO, GameState.HABILIDADES):
            self._desenhar_run()
            if self.state == GameState.PAUSADO:
                self._desenhar_pausa()
            elif self.state == GameState.HABILIDADES:
                self.upgrade_menu.draw(self.screen, self.run_progression, self.multiplayer)
        elif self.state == GameState.GAME_OVER:
            self._desenhar_run()
            self.game_over_screen.draw(self.screen, self.run_state)
        elif self.state == GameState.SALA_EVOLUCAO:
            self.evolution_menu.draw(self.screen, self.progression, self.run_state)

    def _desenhar_run(self):
        shake_x = random.randint(-7, 7) if self.terremoto_timer > 0 else 0
        shake_y = random.randint(-5, 5) if self.terremoto_timer > 0 else 0

        fundo = self.boss_background if self.run_state.fase_atual == 2 else self.background
        fundo.draw(self.screen, self.camera_x + shake_x)
        cam = int(self.camera_x) - shake_x

        cor_plat = settings.COLOR_BOSS_PLATFORM if self.run_state.fase_atual == 2 else settings.COLOR_PLATFORM
        cor_topo = settings.COLOR_BOSS_PLATFORM_TOP if self.run_state.fase_atual == 2 else settings.COLOR_PLATFORM_TOP
        for plat in self.level_manager.plataformas:
            r = plat.copy()
            r.x -= cam
            r.y += shake_y
            pygame.draw.rect(self.screen, cor_plat, srect(r))
            pygame.draw.rect(self.screen, cor_topo, srect(r.x, r.y, r.width, 6))

        if self.porta_rect:
            pr = self.porta_rect.copy()
            pr.x -= cam
            pr.y += shake_y
            dpr = srect(pr)
            pygame.draw.rect(self.screen, (36, 14, 48), dpr, border_radius=sval(8))
            pygame.draw.rect(self.screen, (220, 70, 95), dpr, width=sval(3), border_radius=sval(8))
            pygame.draw.rect(self.screen, (150, 30, 55), dpr.inflate(-sval(14), -sval(14)), border_radius=sval(5))
            fonte_p = font(14, bold=True)
            lbl = fonte_p.render("[E] ENTRAR", True, (255, 225, 230))
            self.screen.blit(lbl, lbl.get_rect(center=(dpr.centerx, dpr.top - sval(14))))

        for inimigo in self.enemies:
            inimigo.draw(self.screen, cam)

        self.player.draw(self.screen, cam)
        if self.multiplayer and self.remote_player:
            self.remote_player.draw(self.screen, cam)
            self._etiqueta_jogador(self.player, cam, "VOCÊ")
            self._etiqueta_jogador(
                self.remote_player,
                cam,
                "JOGADOR 2" if self.lan_role == "host" else "ANFITRIÃO",
            )

        self.hud.draw(self.screen, self.player, self.run_state)
        if self.state == GameState.RUN:
            self.upgrade_menu.desenhar_botao_hud(self.screen, self.run_progression)

        if self.aviso_chefe_timer > 0 or self.terremoto_timer > 0:
            fonte_aviso = font(30, bold=True)
            txt = fonte_aviso.render("O CHEFE ESTÁ AGUARDANDO", True, (255, 85, 95))
            caixa = txt.get_rect(center=spt(settings.SCREEN_WIDTH // 2, 125))
            fundo_msg = caixa.inflate(sval(36), sval(20))
            s = pygame.Surface(fundo_msg.size, pygame.SRCALPHA)
            s.fill((15, 5, 18, 215))
            self.screen.blit(s, fundo_msg.topleft)
            pygame.draw.rect(self.screen, (235, 70, 85), fundo_msg, width=sval(2), border_radius=sval(8))
            self.screen.blit(txt, caixa)

        if self.em_teste:
            fonte = font(16, bold=True)
            tag = fonte.render("MODO TESTE - ESC para voltar ao editor", True, (240, 230, 255))
            caixa = pygame.Rect(
                sval(12),
                sval(settings.SCREEN_HEIGHT - 32),
                tag.get_width() + sval(20),
                sval(26),
            )
            pygame.draw.rect(self.screen, (48, 31, 75), caixa, border_radius=sval(5))
            self.screen.blit(tag, (caixa.x + sval(10), caixa.y + sval(4)))

    def _etiqueta_jogador(self, player, cam, texto):
        fonte = font(14, bold=True)
        render = fonte.render(texto, True, (245, 230, 255))
        x = player.rect.centerx - cam
        self.screen.blit(render, render.get_rect(center=spt(x, player.rect.top - 17)))

    def _desenhar_lobby(self):
        self.background.draw(self.screen, 0)
        fundo = pygame.Surface(sdim(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        fundo.fill((9, 7, 22, 165))
        self.screen.blit(fundo, (0, 0))
        titulo = font(37, bold=True)
        fonte = font(20)
        linhas = [
            "MULTIPLAYER LAN",
            self.lan_message,
            "Esperando outro jogador..." if self.lan_role == "host" else "Aguardando resposta do servidor...",
            "ESC - Cancelar e voltar ao menu",
        ]
        for idx, linha in enumerate(linhas):
            txt = (titulo if idx == 0 else fonte).render(linha, True, (244, 222, 255))
            self.screen.blit(txt, txt.get_rect(center=spt(settings.SCREEN_WIDTH // 2, 150 + idx * 65)))

    def _desenhar_pausa(self):
        overlay = pygame.Surface(sdim(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 4, 19, 195))
        self.screen.blit(overlay, (0, 0))

        opcoes = self._opcoes_pausa()
        painel = srect(0, 0, 410, 325 if self.em_teste else 270)
        painel.center = spt(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 9)
        pygame.draw.rect(self.screen, (24, 17, 44), painel, border_radius=sval(14))
        pygame.draw.rect(self.screen, (126, 87, 170), painel, width=sval(2), border_radius=sval(14))

        titulo = font(38, bold=True)
        texto = titulo.render("PAUSADO", True, (246, 222, 255))
        self.screen.blit(texto, texto.get_rect(center=(painel.centerx, painel.top + sval(48))))

        fonte_botao = font(21, bold=True)
        mouse = mouse_pos()
        for i, (_, rotulo, rect) in enumerate(opcoes):
            destaque = rect.collidepoint(mouse) or i == self.pausa_selecionado
            cor = (75, 43, 106) if destaque else (36, 27, 60)
            borda = (224, 151, 255) if destaque else (116, 83, 151)
            drect = srect(rect)
            pygame.draw.rect(self.screen, cor, drect, border_radius=sval(8))
            pygame.draw.rect(self.screen, borda, drect, width=sval(2), border_radius=sval(8))
            texto = fonte_botao.render(rotulo, True, (246, 232, 255))
            self.screen.blit(texto, texto.get_rect(center=drect.center))

        rodape = (
            "Pausa local: a partida LAN continua"
            if self.multiplayer
            else "ESC: continuar  |  Setas + ENTER: selecionar"
        )
        fonte_pequena = font(14)
        detalhe = fonte_pequena.render(rodape, True, (206, 189, 226))
        self.screen.blit(
            detalhe,
            detalhe.get_rect(center=(painel.centerx, painel.bottom - sval(20))),
        )
