"""Teste de regressão: mobs sobem plataformas sólidas por suas bordas."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
try:
    import pygame
except ImportError:
    pygame = None


@unittest.skipUnless(pygame is not None, "pygame não instalado")
class TestEnemyAI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_quatro_mobs_alcancam_uma_plataforma(self):
        from entities.enemy import Enemy
        plataformas = [pygame.Rect(0, 460, 3600, 40), pygame.Rect(260, 360, 160, 24)]

        class Alvo:
            rect = pygame.Rect(330, 316, 28, 44)
            def receber_dano(self, dano):
                pass

        for tipo in ("basico", "rapido", "resistente", "distancia"):
            with self.subTest(tipo=tipo):
                enemy = Enemy(100, 460 - {"basico": 38, "rapido": 30, "resistente": 46, "distancia": 34}[tipo], tipo)
                enemy.on_ground = True
                chegou = False
                for _ in range(600):
                    enemy.atualizar_ia(1 / 60, Alvo(), plataformas, (0, 3600))
                    if enemy.on_ground and enemy.rect.bottom == 360:
                        chegou = True
                        break
                self.assertTrue(chegou, f"O mob {tipo} não subiu na plataforma")


if __name__ == "__main__":
    unittest.main()
