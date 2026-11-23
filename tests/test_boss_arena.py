"""Regressão da arena exclusiva e dos marcadores do editor."""
import os
import unittest

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
try:
    import pygame
except ImportError:
    pygame = None


@unittest.skipUnless(pygame is not None, 'pygame não instalado')
class TestBossArena(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1,1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_marcador_nao_cria_chefe_entre_mobs(self):
        from game.level_manager import LevelManager
        from levels.level_data import mapa_padrao
        mapa=mapa_padrao()
        mapa['inimigos'] = [
            {'tipo':'distancia','x':400,'y':400},
            {'tipo':'chefe','x':1000,'y':340},
        ]
        level=LevelManager()
        level.carregar_mapa(mapa)
        self.assertEqual(level.portal_x,1000)
        self.assertEqual([e.tipo for e in level.criar_inimigos_iniciais()],['distancia'])
        self.assertFalse(level.chefe_spawnado)

    def test_portal_isola_arena_impede_spawn_e_retorna(self):
        from game.level_manager import LevelManager
        level=LevelManager()
        rect=pygame.Rect(level.portal_x,416,28,44)
        jogador=type('PlayerStub',(),{'rect':rect,'morto':False})()
        self.assertFalse(level.portal_atingido([jogador], 0))
        self.assertTrue(level.portal_atingido([jogador], 10))
        antigas=list(level.plataformas)
        self.assertTrue(level.entrar_arena_chefe())
        self.assertEqual(level.limites,(0,1400))
        self.assertEqual(len(level.plataformas),3)
        self.assertIsNone(level.atualizar_spawner(4,50,800,[]))
        self.assertEqual(level.criar_chefe().tipo,'chefe')
        self.assertIsNone(level.criar_chefe())
        self.assertTrue(level.sair_arena_chefe())
        self.assertEqual(level.plataformas,antigas)
        self.assertFalse(level.portal_atingido([jogador], 10))
        self.assertTrue(level.portal_atingido([jogador], 20))


if __name__=='__main__':
    unittest.main()
