"""Regressões da física do salto, plataformas e alinhamento do piso.

Execute: python -m unittest discover -s tests -p "test_pulo_alinhamento.py" -v
"""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
try:
    import pygame
except ImportError:
    pygame = None


@unittest.skipUnless(pygame is not None, "Pygame não instalado")
class TestPuloEAlinhamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def _player(self, x=300, y=None):
        from config import settings
        from entities.player import Player
        from systems.progression import Progression
        if y is None:
            y = settings.GROUND_Y - Player.HEIGHT
        p = Player(x, y, Progression(carregar=False, persistir=False))
        p.on_ground = True
        return p

    def _plataformas(self):
        from config import settings
        return [pygame.Rect(260, 360, 160, 24),
                pygame.Rect(520, 300, 140, 24),
                pygame.Rect(0, settings.GROUND_Y, 3600,
                            settings.SCREEN_HEIGHT - settings.GROUND_Y)]

    def test_pulo_alcanca_primeira_plataforma_por_baixo(self):
        from config import settings
        p = self._player(x=300)
        p.vy = -settings.JUMP_POWER
        p.on_ground = False
        chegou = False
        for _ in range(120):
            p.update(1 / 60, self._plataformas(), (0, 3600))
            if p.on_ground:
                self.assertEqual(p.rect.bottom, 360)
                chegou = True
                break
        self.assertTrue(chegou, "O ninja não aterrissou na primeira plataforma")

    def test_pulo_alcanca_plataforma_a_186_pixels_do_chao(self):
        from config import settings
        p = self._player(x=570)
        p.vy = -settings.JUMP_POWER
        p.on_ground = False
        for _ in range(120):
            p.update(1 / 60, self._plataformas(), (0, 3600))
            if p.on_ground:
                self.assertEqual(p.rect.bottom, 300)
                return
        self.fail("O ninja não conseguiu aterrissar na plataforma de y=300")

    def test_spawn_antigo_abaixo_do_piso_e_corrigido(self):
        from config import settings
        p = self._player(x=100, y=settings.GROUND_Y - 20)
        p.update(1 / 60, self._plataformas(), (0, 3600))
        self.assertTrue(p.on_ground)
        self.assertEqual(p.rect.bottom, settings.GROUND_Y)

    def test_todos_os_mobs_surgem_no_mesmo_piso(self):
        from config import settings
        from game.level_manager import LevelManager
        from unittest.mock import patch
        level = LevelManager()
        for tipo in ("basico", "rapido", "resistente", "distancia"):
            with self.subTest(tipo=tipo):
                with patch.object(level, "_tipo_aleatorio", return_value=tipo):
                    mob = level._spawnar_inimigo(0, 500)
                self.assertEqual(mob.rect.bottom, settings.GROUND_Y)
                self.assertTrue(mob.on_ground)


if __name__ == "__main__":
    unittest.main()
