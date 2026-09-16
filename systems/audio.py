"""Gerenciador de áudio. Ainda NÃO tem aúdio, deve procurar baixar e colocar """

import os
import pygame

try:
    import numpy as np
    NUMPY_OK = True
except ImportError:
    NUMPY_OK = False

class AudioManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False

        if self.enabled and NUMPY_OK:
            self._gerar_sons()

    def _tom(self, freq=440, duracao=0.08, volume=0.25):
        sample_rate = 44100
        n_samples = int(sample_rate * duracao)
        t = np.linspace(0, duracao, n_samples, False)
        onda = np.sin(freq * t * 2 * np.pi)
        envelope = np.linspace(1, 0, n_samples)
        onda = onda * envelope * volume
        audio = np.int16(onda * 32767)
        stereo = np.column_stack([audio, audio])
        return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))

    def _gerar_sons(self):
        try:
            self.sounds["sword"] = self._tom(520, 0.07)
            self.sounds["shuriken"] = self._tom(760, 0.06)
            self.sounds["hit"] = self._tom(180, 0.09)
            self.sounds["enemy_death"] = self._tom(300, 0.12)
            self.sounds["player_hurt"] = self._tom(140, 0.12)
            self.sounds["player_death"] = self._tom(90, 0.4)
            self.sounds["jump"] = self._tom(600, 0.05)
            self.sounds["upgrade"] = self._tom(880, 0.15)
            self.sounds["menu"] = self._tom(440, 0.05)
        except Exception:
            self.sounds = {}

    def play(self, nome):
        if not self.enabled:
            return
        som = self.sounds.get(nome)
        if som:
            try:
                som.play()
            except pygame.error:
                pass

    def carregar_arquivo(self, nome, caminho):
        if not self.enabled or not os.path.exists(caminho):
            return
        try:
            self.sounds[nome] = pygame.mixer.Sound(caminho)
        except pygame.error:
            pass
