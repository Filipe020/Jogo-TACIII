"""Testes de regressão das opções de áudio e do piso invisível.

Execute: python -m unittest tests.test_som_chao
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pygame
from config import settings
from game.level_manager import LevelManager
from levels.level_data import mapa_padrao, mapa_novo, normalizar_mapa
from systems.audio import AudioManager


class GroundTests(unittest.TestCase):
    def test_novo_mapa_sem_chao_visivel(self):
        self.assertEqual(mapa_novo()["plataformas"], [])

    def test_mapas_antigos_perdem_plataforma_inteira_do_chao(self):
        mapa = mapa_novo()
        mapa["plataformas"] = [[0, 460, 3600, 40], [260, 360, 160, 24]]
        self.assertEqual(normalizar_mapa(mapa)["plataformas"], [[260, 360, 160, 24]])

    def test_fisica_mantem_piso_invisivel(self):
        fase = LevelManager()
        self.assertIn(fase.chao, fase.plataformas)
        self.assertEqual(fase.chao.top, settings.GROUND_Y)
        self.assertEqual(fase.chao.width, mapa_padrao()["largura"])
        fase.entrar_arena_chefe()
        self.assertEqual(fase.chao.width, fase.ARENA_LARGURA)
        fase.sair_arena_chefe()
        self.assertEqual(fase.chao.width, mapa_padrao()["largura"])


class AudioTests(unittest.TestCase):
    def test_mutar_e_salvar_sem_mixer(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = str(Path(pasta) / "audio_settings.json")
            with patch.object(settings, "SOUND_SETTINGS_FILE", caminho):
                with patch.object(pygame.mixer, "init", side_effect=pygame.error("sem audio")):
                    audio = AudioManager()
                    self.assertFalse(audio.muted)
                    audio.set_muted(True)
                    self.assertTrue(AudioManager._ler_som_desligado())
                    audio.play("jump")
                    audio.set_muted(False)
                    self.assertFalse(AudioManager._ler_som_desligado())


if __name__ == "__main__":
    unittest.main()
