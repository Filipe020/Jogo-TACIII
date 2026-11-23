"""Testes da sequência dos quatro bosses e do ataque espectral."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
try:
    import pygame
except ImportError:
    pygame = None


@unittest.skipUnless(pygame is not None, "pygame não instalado")
class TestQuartoChefe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_ordem_dos_quatro_chefes(self):
        from config import settings
        from game.level_manager import LevelManager

        level = LevelManager()
        sequencia = ["chefe", "boss_basico", "boss_distancia", "boss_resistente", "chefe"]
        for etapa, tipo in enumerate(sequencia):
            meta = (etapa + 1) * 10
            self.assertEqual(level.tipo_chefe_atual(), tipo)
            self.assertFalse(level.portal_disponivel(meta - 1))
            self.assertTrue(level.portal_disponivel(meta))
            self.assertTrue(level.entrar_arena_chefe())
            chefe = level.criar_chefe()
            self.assertEqual(chefe.tipo, tipo)
            self.assertTrue(chefe.is_boss)
            self.assertIsNone(level.criar_chefe())
            self.assertEqual(chefe.rect.bottom, settings.GROUND_Y)
            self.assertTrue(level.sair_arena_chefe())

    def test_sprite_quarto_chefe_e_vida(self):
        from entities.enemy import Enemy

        chefe = Enemy(500, 300, "boss_resistente")
        self.assertEqual(chefe.frame_size, (108, 132))
        self.assertEqual(chefe.max_health, 420)
        self.assertEqual(chefe.anim.estado_atual, "idle")

    def test_pulso_avisa_acerta_uma_vez_e_permite_esquivar(self):
        from entities.enemy import Enemy

        class PlayerStub:
            def __init__(self, x):
                self.rect = pygame.Rect(x, 430, 28, 44)
                self.morto = False
                self.dano_recebido = 0

            def receber_dano(self, dano):
                self.dano_recebido += dano

        chefe = Enemy(700, 370, "boss_resistente")
        jogadores = [PlayerStub(800), PlayerStub(850)]
        chefe.pulso_cooldown = 0
        chefe._atualizar_pulso_espectral(0.1, jogadores)
        self.assertGreater(chefe.pulso_carga, 0)
        for _ in range(8):
            chefe._atualizar_pulso_espectral(0.1, jogadores)
        self.assertEqual([p.dano_recebido for p in jogadores], [16, 16])
        for _ in range(10):
            chefe._atualizar_pulso_espectral(0.1, jogadores)
        self.assertEqual([p.dano_recebido for p in jogadores], [16, 16])

        chefe.pulso_carga = 0
        chefe.pulso_cooldown = 0
        chefe._atualizar_pulso_espectral(0.1, jogadores)
        for p in jogadores:
            p.rect.x += 1000
        for _ in range(8):
            chefe._atualizar_pulso_espectral(0.1, jogadores)
        self.assertEqual([p.dano_recebido for p in jogadores], [16, 16])


if __name__ == "__main__":
    unittest.main()
