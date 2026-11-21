"""Testes de estados do menu de pausa (sem abrir janela Pygame)."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pygame

from game.game_manager import GameManager
from game.game_state import GameState


class PauseMenuTests(unittest.TestCase):
    def make_game(self, *, test=False, multiplayer=False):
        game = GameManager.__new__(GameManager)
        game.state = GameState.RUN
        game.em_teste = test
        game.multiplayer = multiplayer
        game.lan_role = "host" if multiplayer else None
        game.lan = None
        game.remote_player = None
        game.remote_actions = {}
        game.pausa_selecionado = 0
        game.main_menu = SimpleNamespace(tela="principal", avisar=Mock())
        game.editor = SimpleNamespace(informar=Mock())
        return game

    def key(self, key):
        return pygame.event.Event(pygame.KEYDOWN, key=key)

    def test_esc_pausa_e_retorna(self):
        game = self.make_game()
        game.handle_event(self.key(pygame.K_ESCAPE))
        self.assertEqual(game.state, GameState.PAUSADO)
        game.handle_event(self.key(pygame.K_ESCAPE))
        self.assertEqual(game.state, GameState.RUN)

    def test_voltar_menu_pelo_teclado(self):
        game = self.make_game()
        game.handle_event(self.key(pygame.K_ESCAPE))
        game.handle_event(self.key(pygame.K_DOWN))
        game.handle_event(self.key(pygame.K_RETURN))
        self.assertEqual(game.state, GameState.MENU)
        self.assertEqual(game.main_menu.tela, "principal")

    def test_voltar_menu_por_clique(self):
        game = self.make_game()
        game.handle_event(self.key(pygame.K_ESCAPE))
        _, _, botao = game._opcoes_pausa()[1]
        game.handle_event(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=botao.center))
        self.assertEqual(game.state, GameState.MENU)

    def test_teste_de_fase_tem_opcao_voltar_ao_editor(self):
        game = self.make_game(test=True)
        game.handle_event(self.key(pygame.K_ESCAPE))
        self.assertEqual([acao for acao, _, _ in game._opcoes_pausa()],
                         ["continuar", "editor", "menu"])
        game.handle_event(self.key(pygame.K_DOWN))
        game.handle_event(self.key(pygame.K_RETURN))
        self.assertEqual(game.state, GameState.EDITOR)
        game.editor.informar.assert_called_once()

    def test_menu_encerrar_lan(self):
        game = self.make_game(multiplayer=True)
        game.lan = SimpleNamespace(close=Mock())
        game.handle_event(self.key(pygame.K_ESCAPE))
        game.handle_event(self.key(pygame.K_DOWN))
        game.handle_event(self.key(pygame.K_RETURN))
        self.assertEqual(game.state, GameState.MENU)
        self.assertFalse(game.multiplayer)
        self.assertEqual(game.main_menu.tela, "principal")

    def test_pausa_host_lan_nao_para_simulacao(self):
        game = self.make_game(multiplayer=True)
        game.state = GameState.PAUSADO
        game._processar_lan = Mock()
        game._atualizar_run = Mock()
        with patch.object(pygame.key, "get_pressed", return_value={}):
            game.update(0.016)
        game._atualizar_run.assert_called_once_with(0.016, {}, paused_local=True)

    def test_pausa_solo_nao_atualiza_simulacao(self):
        game = self.make_game()
        game.state = GameState.PAUSADO
        game._processar_lan = Mock()
        game._atualizar_run = Mock()
        with patch.object(pygame.key, "get_pressed", return_value={}):
            game.update(0.016)
        game._atualizar_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
