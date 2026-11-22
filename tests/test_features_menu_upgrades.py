"""Testes de menu, aquisição de habilidades e integração com o gerenciador.

Para executar: python -m unittest discover -s tests -v
"""
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pygame

from config import settings
from game.game_manager import GameManager
from game.game_state import GameState
from systems.progression import Progression
from ui.main_menu import MainMenu
from ui.upgrade_menu import UpgradeMenu
from entities.player import Player


class MenuAndUpgradeTests(unittest.TestCase):
    @staticmethod
    def key(key):
        return pygame.event.Event(pygame.KEYDOWN, key=key)

    def test_menu_opcao_sair_retorna_acao(self):
        menu = MainMenu.__new__(MainMenu)
        menu.tela = "principal"
        menu.botoes = [("Sair do Jogo", pygame.Rect(0, 0, 140, 40))]
        menu.ip_ativo = False
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20))
        self.assertEqual(menu.handle_event(event, tem_save=False), "sair")

    def test_gerenciador_sinaliza_encerramento(self):
        game = GameManager.__new__(GameManager)
        game.state = GameState.MENU
        game.main_menu = SimpleNamespace(handle_event=Mock(return_value="sair"))
        game.sair_solicitado = False
        game.handle_event(self.key(pygame.K_RETURN))
        self.assertTrue(game.sair_solicitado)

    def test_novo_jogo_reseta_save_antes_de_criar_personagem(self):
        game = GameManager.__new__(GameManager)
        game.state = GameState.MENU
        game.main_menu = SimpleNamespace(handle_event=Mock(return_value="novo_jogo"))
        game.progression = Mock()
        ordem = []
        game.progression.reiniciar_novo_jogo.side_effect = lambda: ordem.append("reset")
        game.iniciar_run = Mock(side_effect=lambda **kwargs: ordem.append("run"))
        game.audio = SimpleNamespace(play=Mock())
        game.handle_event(self.key(pygame.K_RETURN))
        self.assertEqual(ordem, ["reset", "run"])

    def test_continuar_nao_reseta_habilidades(self):
        game = GameManager.__new__(GameManager)
        game.state = GameState.MENU
        game.main_menu = SimpleNamespace(handle_event=Mock(return_value="continuar"))
        game.progression = Mock()
        game.iniciar_run = Mock()
        game.audio = SimpleNamespace(play=Mock())
        game.handle_event(self.key(pygame.K_RETURN))
        game.progression.reiniciar_novo_jogo.assert_not_called()
        game.iniciar_run.assert_called_once()

    def test_h_abre_e_fecha_menu_de_habilidades(self):
        game = GameManager.__new__(GameManager)
        game.state = GameState.RUN
        game.upgrade_menu = UpgradeMenu()
        game.handle_event(self.key(pygame.K_h))
        self.assertEqual(game.state, GameState.HABILIDADES)
        game.handle_event(self.key(pygame.K_h))
        self.assertEqual(game.state, GameState.RUN)

    def test_botao_hud_abre_menu_de_habilidades(self):
        game = GameManager.__new__(GameManager)
        game.state = GameState.RUN
        game.upgrade_menu = UpgradeMenu()
        pos = UpgradeMenu.HUD_RECT.center
        game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
        self.assertEqual(game.state, GameState.HABILIDADES)

    def test_upgrade_aplica_bonus_ao_jogador_na_hora(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(settings, "SAVE_FILE", tmp + "/save.json"):
                game = GameManager.__new__(GameManager)
                game.upgrade_menu = UpgradeMenu()
                game.run_progression = Progression(carregar=False, persistir=False)
                game.run_progression.pontos_disponiveis = 10
                game.multiplayer = False
                game.player = SimpleNamespace(aplicar_melhorias=Mock())
                game.remote_player = None
                game.audio = SimpleNamespace(play=Mock())
                self.assertTrue(game._comprar_habilidade("vida_maxima"))
                self.assertEqual(game.run_progression.pontos_disponiveis, 5)
                game.player.aplicar_melhorias.assert_called_once()
                self.assertEqual(game.run_progression.niveis["vida_maxima"], 1)

    def test_bonus_preserva_vida_e_aumenta_maximo(self):
        progress = Progression(carregar=False, persistir=False)
        player = Player.__new__(Player)
        player.progression = progress
        player.max_health = 100
        player.health = 45
        player.speed = settings.MOVE_SPEED
        player.shurikens_max = 5
        player.shurikens = 2
        player.cooldown_espada_base = 0.5
        player.cooldown_shuriken_base = 0.6
        player.sword = SimpleNamespace(cooldown=0.5)
        player.shuriken_weapon = SimpleNamespace(cooldown=0.6)
        progress.niveis["vida_maxima"] = 1
        progress.niveis["qtd_shurikens"] = 1
        progress.niveis["velocidade"] = 1
        player.aplicar_melhorias()
        self.assertEqual((player.max_health, player.health), (120, 65))
        self.assertEqual((player.shurikens_max, player.shurikens), (6, 3))
        self.assertGreater(player.speed, settings.MOVE_SPEED)


if __name__ == "__main__":
    unittest.main()
