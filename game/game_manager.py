"""Controla o estado geral do jogo: menu, Run, pausa, morte e Sala de Evolução"""

import pygame
import os

from game.game_state import GameState, RunState
from game.level_manager import LevelManager
from entities.player import Player
from entities.enemy import Enemy, BOSS_TYPES
from entities.projectile import Projectile
from network.lan import LANPeer, PORT, local_ip
from levels.level_data import normalizar_mapa
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
from levels.level_data import carregar_slot, mapa_padrao
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
        self.editor = LevelEditor(self.background)
        self.em_teste = False

        self.main_menu = MainMenu()
        self.main_menu.som_ativo = not self.audio.muted
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
        self.aviso_chefe_timer = 0.0
        self.chefe_vitoria_timer = 0.0
        self.mensagem_pos_chefe = 0.0
        self._inimigos_antes_arena = []
        self._retorno_arena = None


    #---Transições de estado---
    def iniciar_run(self, mapa=None, teste=False, multiplayer=False):
        """ENTER usa o slot salvo; F5 usa inclusive alterações ainda não salvas."""
        if mapa is None:
            try:
                mapa = carregar_slot(self.editor.slot) or mapa_padrao()
            except (ValueError, OSError, KeyError, TypeError):
                mapa = mapa_padrao()
        mapa = normalizar_mapa(mapa)
        self.level_manager.carregar_mapa(mapa)
        self.run_state.reiniciar()
        self.multiplayer = multiplayer
        # Testes do editor e LAN não modificam o save solo do jogador.
        self.run_progression = (Progression(carregar=False, persistir=False)
                                if teste or multiplayer else self.progression)
        spawn_x, spawn_y = self.level_manager.spawn_jogador
        self.player = Player(spawn_x + (68 if multiplayer and self.lan_role == "client" else 0),
                             spawn_y, self.run_progression)
        self.remote_player = None
        if multiplayer:
            self.remote_player = Player(spawn_x + (0 if self.lan_role == "client" else 68),
                                        spawn_y, self.run_progression)
        self.client_enemies = {}
        self.enemies = self.level_manager.criar_inimigos_iniciais()
        self.aviso_chefe_timer = 0.0
        self.chefe_vitoria_timer = 0.0
        self.mensagem_pos_chefe = 0.0
        self._inimigos_antes_arena = []
        self._retorno_arena = None
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
        self.lan_message = (f"Sala criada! IP: {local_ip()}  Porta: {PORT}" if role == "host"
                            else f"Conectando a {address}:{PORT}...")
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
            # O cliente pausado continua recebendo o mundo, mas não envia ações.
            self.lan.send({"type": "input", "actions": {
                "left": self.state == GameState.RUN and bool(keys[pygame.K_a]),
                "right": self.state == GameState.RUN and bool(keys[pygame.K_d]),
                "jump": self.state == GameState.RUN and bool(keys[pygame.K_w] or keys[pygame.K_SPACE]),
                "sword": self.state == GameState.RUN and bool(buttons[0]),
                "shuriken": self.state == GameState.RUN and bool(buttons[2]),
            }})

    @staticmethod
    def _dados_proj(proj):
        return [round(proj.x, 2), round(proj.y, 2), int(proj.facing)]

    @staticmethod
    def _dados_player(player):
        return {
            "x": round(player.x, 2), "y": round(player.y, 2),
            "vx": round(player.vx, 2), "vy": round(player.vy, 2),
            "facing": player.facing, "health": player.health, "max_health": player.max_health,
            "shurikens": player.shurikens, "shurikens_max": player.shurikens_max,
            "morto": player.morto, "invulneravel": round(player.invulneravel_timer, 2),
            "anim": player.anim.estado_atual, "attack": round(player.ataque_visual_timer, 2),
            "projectiles": [GameManager._dados_proj(proj) for proj in player.projectiles if proj.alive],
        }

    def _criar_snapshot(self):
        return {
            "type": "snapshot", "kills": self.run_state.inimigos_derrotados,
            "mobs_kills": self.run_state.mobs_derrotados,
            "portal_target": self.level_manager.proximo_portal_mobs,
            "boss_index": self.level_manager.boss_index,
            "boss_arena": self.level_manager.arena_ativa,
            "boss_victory_time": round(self.chefe_vitoria_timer, 2),
            "upgrades": self.run_progression.estado_rede(),
            "players": [self._dados_player(self.player), self._dados_player(self.remote_player)],
            "enemies": [{
                "id": e.uid, "tipo": e.tipo, "x": round(e.x, 2), "y": round(e.y, 2),
                "facing": e.facing, "health": e.health, "alive": e.alive,
                "anim": e.anim.estado_atual,
                "pulse_charge": round(e.pulso_carga, 2),
                "pulse_effect": round(e.pulso_efeito, 2),
                "projectiles": [self._dados_proj(p) for p in e.projectiles if p.alive],
            } for e in self.enemies],
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
        # O anfitrião decide quando os jogadores entram e saem da arena.
        arena_remota = bool(dados.get("boss_arena", False))
        if arena_remota and not self.level_manager.arena_ativa:
            self.level_manager.entrar_arena_chefe()
            self.camera_x = 0.0
        elif not arena_remota and self.level_manager.arena_ativa:
            self.level_manager.sair_arena_chefe()
            self.mensagem_pos_chefe = 5.0
        self.chefe_vitoria_timer = float(dados.get("boss_victory_time", 0.0))
        # O cliente é o player 2. Os índices sempre se referem a host e convidado.
        self._aplicar_player(self.remote_player, dados["players"][0])
        self._aplicar_player(self.player, dados["players"][1])
        self.run_state.inimigos_derrotados = int(dados["kills"])
        self.run_state.mobs_derrotados = max(0, int(dados.get("mobs_kills", dados["kills"])))
        # O servidor é a referência para as metas, inclusive depois da arena.
        self.level_manager.proximo_portal_mobs = max(10, int(
            dados.get("portal_target", self.level_manager.proximo_portal_mobs)))
        # Mesmo após várias arenas, o cliente precisa exibir o chefe certo.
        self.level_manager.boss_index = int(dados.get("boss_index", self.level_manager.boss_index)) % len(self.level_manager.boss_order)
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
            e.pulso_carga = max(0.0, float(item.get("pulse_charge", 0.0)))
            e.pulso_efeito = max(0.0, float(item.get("pulse_effect", 0.0)))
            e.projectiles = self._restaurar_proj(item["projectiles"], False)
            vivos[uid] = e
        self.client_enemies = vivos
        self.enemies = list(vivos.values())

    def _atualizar_cliente(self, dt):
        # Snapshots do host: o cliente não executa física nem combate localmente.
        if self.player is None:
            return
        self.player.anim.atualizar(dt)
        self.remote_player.anim.atualizar(dt)
        for enemy in self.enemies:
            enemy.anim.atualizar(dt)
        self.mensagem_pos_chefe = max(0.0, self.mensagem_pos_chefe - dt)
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
            (acao, rotulo, pygame.Rect(
                (settings.SCREEN_WIDTH - largura) // 2,
                inicio + i * (altura + espacamento), largura, altura,
            ))
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
            elif acao == "alternar_som":
                self.audio.set_muted(not self.audio.muted)
                self.main_menu.som_ativo = not self.audio.muted
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
            # F8 leva à arena exclusiva do chefe sem precisar alcançar o portal.
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_F8
                    and self.lan_role != "client"):
                self._spawnar_chefe(forcar=True)  # atalho de teste, ignora a meta
                return
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
            # Multiplayer: pausa apenas os controles locais; a simulação do host
            # continua para não congelar o outro jogador na rede.
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

    def _spawnar_chefe(self, forcar=False):
        """Inicia encontro isolado; F8 pode forçar a entrada para depuração."""
        if self.player is None:
            return None
        if not forcar and not self.level_manager.portal_disponivel(
                self.run_state.mobs_derrotados):
            return None
        if not self.level_manager.entrar_arena_chefe():
            return None
        jogadores = [p for p in (self.player, self.remote_player) if p is not None]
        self._retorno_arena = [(p.x, p.y) for p in jogadores]
        self._inimigos_antes_arena = self.enemies
        self.enemies = []
        for indice, jogador in enumerate(jogadores):
            jogador.x = 120 + indice * 70
            jogador.y = settings.GROUND_Y - jogador.height
            jogador.vx = 0
            jogador.vy = 0
            jogador.on_ground = True
            jogador.projectiles.clear()
        self.camera_x = 0.0
        self.chefe_vitoria_timer = 0.0
        chefe = self.level_manager.criar_chefe(self.player.x)
        if chefe is not None:
            self.enemies.append(chefe)
            self.aviso_chefe_timer = 4.0
        return chefe

    def _terminar_encontro_chefe(self):
        """Volta à fase original sem misturar os mobs com a luta do chefe."""
        if not self.level_manager.sair_arena_chefe():
            return
        jogadores = [p for p in (self.player, self.remote_player) if p is not None]
        for i, jogador in enumerate(jogadores):
            if self._retorno_arena and i < len(self._retorno_arena):
                jogador.x, jogador.y = self._retorno_arena[i]
            jogador.vx = 0
            jogador.vy = 0
            jogador.projectiles.clear()
        self.enemies = [e for e in self._inimigos_antes_arena if e.alive]
        self._inimigos_antes_arena = []
        self._retorno_arena = None
        self.chefe_vitoria_timer = 0.0
        self.mensagem_pos_chefe = 5.0
        self.camera_x = max(0, min(self.player.x - settings.SCREEN_WIDTH // 2,
                                   max(0, self.level_manager.limites[1] - settings.SCREEN_WIDTH)))

    def _atualizar_run(self, dt, keys, paused_local=False):
        self.run_state.tempo_de_run += dt
        self.aviso_chefe_timer = max(0, self.aviso_chefe_timer - dt)
        self.mensagem_pos_chefe = max(0, self.mensagem_pos_chefe - dt)

        if paused_local:
            self.player.handle_actions({}, self.audio)
        else:
            self.player.handle_input(keys, self.audio)
        self.player.update(dt, self.level_manager.plataformas, self.level_manager.limites)
        if self.multiplayer and self.remote_player:
            self.remote_player.handle_actions(self.remote_actions, self.audio)
            self.remote_player.update(dt, self.level_manager.plataformas, self.level_manager.limites)

        if self.level_manager.portal_atingido(
                (self.player, self.remote_player), self.run_state.mobs_derrotados):
            self._spawnar_chefe()

        if not self.level_manager.arena_ativa:
            novo_inimigo = self.level_manager.atualizar_spawner(
                dt, self.run_state.tempo_de_run, self.player.x, self.enemies
            )
            if novo_inimigo:
                self.enemies.append(novo_inimigo)

        for inimigo in self.enemies:
            alvos = [p for p in (self.player, self.remote_player) if p is not None and not p.morto]
            if alvos:
                alvo = min(alvos, key=lambda p: abs(p.rect.centerx - inimigo.rect.centerx) + abs(p.rect.centery - inimigo.rect.centery))
                inimigo.atualizar_ia(dt, alvo, self.level_manager.plataformas,
                                   self.level_manager.limites, alvos)

        self._resolver_combate()
        # Mantém o inimigo na cena até a animação de morte terminar de tocar.
        self.enemies = [e for e in self.enemies if not e.animacao_morte_terminou()]

        if self.level_manager.arena_ativa:
            if any(e.tipo in BOSS_TYPES and e.alive for e in self.enemies):
                self.chefe_vitoria_timer = 0.0
            else:
                self.chefe_vitoria_timer += dt
                if self.chefe_vitoria_timer >= 2.4:
                    self._terminar_encontro_chefe()

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

    def _registrar_eliminacao(self, inimigo):
        """Credita a eliminação e soma para o portal apenas mobs normais."""
        self.run_progression.registrar_kill_run(self.run_state)
        if inimigo.tipo not in BOSS_TYPES:
            self.run_state.mobs_derrotados += 1

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
                            self._registrar_eliminacao(inimigo)
            for proj in jogador.projectiles:
                if not proj.alive:
                    continue
                for inimigo in self.enemies:
                    if inimigo.alive and proj.rect.colliderect(inimigo.rect):
                        inimigo.receber_dano(proj.damage, self.audio)
                        proj.alive = False
                        if not inimigo.alive:
                            self._registrar_eliminacao(inimigo)
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
        self.background.draw(self.screen, self.camera_x)
        cam = int(self.camera_x)
        if self.level_manager.arena_ativa:
            self._desenhar_arena_chefe()
        elif self.level_manager.portal_disponivel(self.run_state.mobs_derrotados):
            self._desenhar_portal_chefe(cam)

        for plat in self.level_manager.plataformas:
            # O chão só existe para colisão; o terreno visível é a arte de fundo.
            if plat is self.level_manager.chao:
                continue
            r = plat.copy()
            r.x -= cam
            pygame.draw.rect(self.screen, settings.COLOR_PLATFORM, r)
            pygame.draw.rect(self.screen, settings.COLOR_PLATFORM_TOP, (r.x, r.y, r.width, 6))

        for inimigo in self.enemies:
            inimigo.draw(self.screen, cam)

        self.player.draw(self.screen, cam)
        if self.multiplayer and self.remote_player:
            self.remote_player.draw(self.screen, cam)
            self._etiqueta_jogador(self.player, cam, "VOCÊ")
            self._etiqueta_jogador(self.remote_player, cam, "JOGADOR 2" if self.lan_role == "host" else "ANFITRIÃO")
        self.hud.draw(self.screen, self.player, self.run_state)
        self._desenhar_meta_portal()
        self._desenhar_barra_chefe()
        if self.chefe_vitoria_timer > 0 and self.level_manager.arena_ativa:
            self._banner_encontro("CHEFE DERROTADO!", (255, 228, 135))
        elif self.mensagem_pos_chefe > 0:
            self._banner_encontro("CHEFE DERROTADO - FASE LIBERADA", (255, 228, 135))
        if self.state == GameState.RUN:
            self.upgrade_menu.desenhar_botao_hud(self.screen, self.run_progression)
        if self.em_teste:
            fonte = pygame.font.SysFont("consolas", 16, bold=True)
            tag = fonte.render("MODO TESTE - ESC para voltar ao editor", True, (240, 230, 255))
            caixa = pygame.Rect(12, settings.SCREEN_HEIGHT - 32, tag.get_width() + 20, 26)
            pygame.draw.rect(self.screen, (48, 31, 75), caixa, border_radius=5)
            self.screen.blit(tag, (caixa.x + 10, caixa.y + 4))

    def _banner_encontro(self, mensagem, cor):
        fonte = pygame.font.SysFont("consolas", 25, bold=True)
        texto = fonte.render(mensagem, True, cor)
        rect = texto.get_rect(center=(settings.SCREEN_WIDTH // 2, 140))
        pygame.draw.rect(self.screen, (34, 19, 48), rect.inflate(25, 17), border_radius=8)
        self.screen.blit(texto, rect)

    def _desenhar_meta_portal(self):
        """Mostra o andamento da próxima meta sem cobrir os controles."""
        if self.level_manager.arena_ativa:
            return
        atual = self.run_state.mobs_derrotados
        meta = self.level_manager.proximo_portal_mobs
        pronto = self.level_manager.portal_disponivel(atual)
        mensagem = ("PORTAL ABERTO! ENCONTRE A ENTRADA" if pronto
                    else f"PORTAL DO CHEFE: {atual}/{meta} MOBS")
        fonte = pygame.font.SysFont("consolas", 15, bold=True)
        texto = fonte.render(mensagem, True, (231, 196, 255) if pronto else (241, 229, 255))
        caixa = pygame.Rect(14, 114, texto.get_width() + 20, 27)
        pygame.draw.rect(self.screen, (31, 20, 49), caixa, border_radius=5)
        self.screen.blit(texto, (caixa.x + 10, caixa.y + 5))

    def _desenhar_portal_chefe(self, cam):
        """Portal localizado ao final da fase (ou onde foi marcado no editor)."""
        px = int(self.level_manager.portal_x - cam)
        if not -90 <= px <= settings.SCREEN_WIDTH + 90:
            return
        topo = settings.GROUND_Y - 142
        pygame.draw.ellipse(self.screen, (54, 22, 99), (px - 34, topo, 68, 142))
        pygame.draw.ellipse(self.screen, (190, 85, 243), (px - 34, topo, 68, 142), 5)
        pygame.draw.ellipse(self.screen, (132, 55, 201), (px - 21, topo + 17, 42, 111), 3)
        for dy in (topo + 33, topo + 59, topo + 88):
            pygame.draw.line(self.screen, (196, 133, 255), (px - 11, dy), (px + 11, dy + 4), 2)
        fonte = pygame.font.SysFont("consolas", 14, bold=True)
        texto = fonte.render("PORTAL DO CHEFE", True, (255, 231, 175))
        self.screen.blit(texto, texto.get_rect(center=(px, topo - 13)))

    def _desenhar_arena_chefe(self):
        """Atmosfera visual própria: nenhuma plataforma da fase principal."""
        filtro = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        filtro.fill((32, 5, 64, 152))
        self.screen.blit(filtro, (0, 0))
        # Colunas e runas demarcam o local separado da luta.
        for x in (35, 225, 445, 665, 885):
            pygame.draw.rect(self.screen, (43, 28, 75), (x, 205, 28, 260))
            pygame.draw.rect(self.screen, (113, 61, 155), (x - 8, 204, 44, 14), 2)
            pygame.draw.line(self.screen, (157, 90, 202), (x + 14, 220), (x + 14, 445), 2)
        pygame.draw.circle(self.screen, (119, 59, 162), (settings.SCREEN_WIDTH // 2, 130), 74, 3)
        fonte = pygame.font.SysFont("consolas", 18, bold=True)
        nome = self.level_manager.nome_chefe_atual()
        texto = fonte.render(f"ARENA DE {nome}", True, (246, 200, 255))
        self.screen.blit(texto, texto.get_rect(center=(settings.SCREEN_WIDTH // 2, 175)))

    def _desenhar_barra_chefe(self):
        chefes = [e for e in self.enemies if e.tipo in BOSS_TYPES and e.alive]
        if chefes:
            chefe = chefes[0]
            largura, altura = 360, 16
            x = (settings.SCREEN_WIDTH - largura) // 2
            y = 70
            nomes = {
                "chefe": "ESPECTRO ANCESTRAL",
                "boss_basico": "NECROZUMBI TITAN",
                "boss_distancia": "SENTINELA MECANICO",
                "boss_resistente": "ESPECTRO DAS CINZAS",
                "boss_samurai": "SAMURAI DO CREPUSCULO",
            }
            cores = {
                "chefe": (166, 74, 211),
                "boss_basico": (180, 96, 96),
                "boss_distancia": (102, 213, 160),
                "boss_resistente": (187, 218, 250),
                "boss_samurai": (214, 95, 132),
            }
            fonte = pygame.font.SysFont("consolas", 17, bold=True)
            texto = fonte.render(f"{nomes.get(chefe.tipo, 'CHEFE')}  -  CHEFE", True, (250, 216, 255))
            self.screen.blit(texto, texto.get_rect(center=(settings.SCREEN_WIDTH // 2, y - 15)))
            pygame.draw.rect(self.screen, (34, 19, 52), (x, y, largura, altura), border_radius=5)
            pct = max(0.0, min(1.0, chefe.health / chefe.max_health))
            if pct > 0:
                pygame.draw.rect(self.screen, cores.get(chefe.tipo, (166, 74, 211)),
                                 (x, y, max(1, int(largura * pct)), altura), border_radius=5)
            pygame.draw.rect(self.screen, (231, 184, 255), (x, y, largura, altura), 2, border_radius=5)
        if self.aviso_chefe_timer > 0 and chefes:
            fonte = pygame.font.SysFont("consolas", 24, bold=True)
            texto = fonte.render("UM CHEFE APARECEU!", True, (255, 199, 99))
            self.screen.blit(texto, texto.get_rect(center=(settings.SCREEN_WIDTH // 2, 117)))

    def _etiqueta_jogador(self, player, cam, texto):
        fonte = pygame.font.SysFont("consolas", 14, bold=True)
        render = fonte.render(texto, True, (245, 230, 255))
        x = player.rect.centerx - cam
        self.screen.blit(render, render.get_rect(center=(x, player.rect.top - 17)))

    def _desenhar_lobby(self):
        self.background.draw(self.screen, 0)
        fundo = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        fundo.fill((9, 7, 22, 165))
        self.screen.blit(fundo, (0, 0))
        titulo = pygame.font.SysFont("consolas", 37, bold=True)
        fonte = pygame.font.SysFont("consolas", 20)
        linhas = ["MULTIPLAYER LAN", self.lan_message,
                  "Esperando outro jogador..." if self.lan_role == "host" else "Aguardando resposta do servidor...",
                  "ESC - Cancelar e voltar ao menu"]
        for idx, linha in enumerate(linhas):
            txt = (titulo if idx == 0 else fonte).render(linha, True, (244, 222, 255))
            self.screen.blit(txt, txt.get_rect(center=(settings.SCREEN_WIDTH // 2, 150 + idx * 65)))

    def _desenhar_pausa(self):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 4, 19, 195))
        self.screen.blit(overlay, (0, 0))

        opcoes = self._opcoes_pausa()
        painel = pygame.Rect(0, 0, 410, 325 if self.em_teste else 270)
        painel.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 9)
        pygame.draw.rect(self.screen, (24, 17, 44), painel, border_radius=14)
        pygame.draw.rect(self.screen, (126, 87, 170), painel, width=2, border_radius=14)

        titulo = pygame.font.SysFont("consolas", 38, bold=True)
        texto = titulo.render("PAUSADO", True, (246, 222, 255))
        self.screen.blit(texto, texto.get_rect(center=(settings.SCREEN_WIDTH // 2, painel.top + 48)))

        fonte_botao = pygame.font.SysFont("consolas", 21, bold=True)
        mouse = settings.posicao_mouse_logica()
        for i, (_, rotulo, rect) in enumerate(opcoes):
            destaque = rect.collidepoint(mouse) or i == self.pausa_selecionado
            cor = (75, 43, 106) if destaque else (36, 27, 60)
            borda = (224, 151, 255) if destaque else (116, 83, 151)
            pygame.draw.rect(self.screen, cor, rect, border_radius=8)
            pygame.draw.rect(self.screen, borda, rect, width=2, border_radius=8)
            texto = fonte_botao.render(rotulo, True, (246, 232, 255))
            self.screen.blit(texto, texto.get_rect(center=rect.center))

        rodape = ("Pausa local: a partida LAN continua" if self.multiplayer
                  else "ESC: continuar  |  Setas + ENTER: selecionar")
        fonte_pequena = pygame.font.SysFont("consolas", 14)
        detalhe = fonte_pequena.render(rodape, True, (206, 189, 226))
        self.screen.blit(detalhe, detalhe.get_rect(center=(
            settings.SCREEN_WIDTH // 2, painel.bottom - 20)))
