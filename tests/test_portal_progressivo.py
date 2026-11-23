"""Regressão: chão alinhado e portal progressivo (10, 20, 30...)."""
import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
try:
    import pygame
except ImportError:
    pygame = None


@unittest.skipUnless(pygame is not None, "pygame não instalado")
class TestPortalProgressivo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_meta_progressiva_e_reiniciar(self):
        from game.level_manager import LevelManager
        from game.game_state import RunState
        nivel = LevelManager()
        run = RunState()
        jogador = SimpleNamespace(rect=pygame.Rect(nivel.portal_x - 10, 430, 28, 44), morto=False)
        self.assertEqual(nivel.proximo_portal_mobs, 10)
        self.assertFalse(nivel.portal_atingido([jogador], run.mobs_derrotados))
        run.mobs_derrotados = 9
        self.assertFalse(nivel.portal_atingido([jogador], 9))
        run.mobs_derrotados = 10
        self.assertTrue(nivel.portal_atingido([jogador], 10))
        self.assertTrue(nivel.entrar_arena_chefe())
        self.assertFalse(nivel.portal_disponivel(20))
        self.assertIsNotNone(nivel.criar_chefe())
        self.assertTrue(nivel.sair_arena_chefe())
        self.assertEqual(nivel.proximo_portal_mobs, 20)
        self.assertFalse(nivel.portal_disponivel(19))
        self.assertTrue(nivel.portal_disponivel(20))
        self.assertTrue(nivel.entrar_arena_chefe())
        self.assertIsNotNone(nivel.criar_chefe())
        self.assertTrue(nivel.sair_arena_chefe())
        self.assertEqual(nivel.proximo_portal_mobs, 30)
        nivel.reiniciar()
        run.reiniciar()
        self.assertEqual(nivel.proximo_portal_mobs, 10)
        self.assertEqual(run.mobs_derrotados, 0)

    def test_portal_so_perto_da_entrada(self):
        from game.level_manager import LevelManager
        nivel = LevelManager()
        longe = SimpleNamespace(rect=pygame.Rect(nivel.portal_x + 120, 430, 28, 44), morto=False)
        self.assertFalse(nivel.portal_atingido([longe], 10))

    def test_kill_do_chefe_nao_conta_para_portal(self):
        from game.game_manager import GameManager
        from game.game_state import RunState
        from systems.progression import Progression
        gerente = GameManager.__new__(GameManager)
        gerente.run_state = RunState()
        gerente.run_progression = Progression(carregar=False, persistir=False)
        gerente._registrar_eliminacao(SimpleNamespace(tipo="basico"))
        gerente._registrar_eliminacao(SimpleNamespace(tipo="chefe"))
        self.assertEqual(gerente.run_state.inimigos_derrotados, 2)
        self.assertEqual(gerente.run_state.mobs_derrotados, 1)
        self.assertEqual(gerente.run_progression.pontos_disponiveis, 2)

    def test_chao_alinhado_e_piso_antigo_oculto(self):
        from config import settings
        from levels.level_data import mapa_novo, normalizar_mapa
        from game.level_manager import LevelManager
        self.assertEqual(settings.GROUND_Y, 486)
        self.assertEqual(mapa_novo()["spawn_jogador"][1] + 44, settings.GROUND_Y)
        nivel = LevelManager()
        self.assertEqual(nivel.chao.top, 486)
        self.assertEqual(normalizar_mapa({**mapa_novo(), "plataformas": [[0,460,3600,40]]})["plataformas"], [])
        self.assertEqual(nivel.entrar_arena_chefe(), True)
        self.assertEqual(nivel.chao.top, 486)

if __name__ == "__main__":
    unittest.main()
