"""Sistema de animação por spritesheet."""

import os
import pygame

class SpriteSheet:
    """Carrega e fatia um spritesheet horizontal em uma lista de frames."""

    _cache = {}

    @classmethod
    def carregar_frames(cls, caminho, frame_w, frame_h, num_frames, cor_placeholder=(200, 60, 200)):
        chave = (caminho, frame_w, frame_h, num_frames)
        if chave in cls._cache:
            return cls._cache[chave]

        if os.path.exists(caminho):
            folha = pygame.image.load(caminho).convert_alpha()
            largura_esperada = frame_w * num_frames
            if folha.get_width() != largura_esperada or folha.get_height() != frame_h:
                print(
                    f"[aviso] {caminho}: a imagem tem {folha.get_width()}x{folha.get_height()}px, "
                    f"mas config/animations.py espera {largura_esperada}x{frame_h}px "
                    f"({num_frames} frames de {frame_w}x{frame_h}). O corte provavelmente vai "
                    f"sair errado — confira o tamanho de cada frame no arquivo exportado, ou "
                    f"ajuste frame_w/frame_h/frames nessa animação."
                )
            frames = []
            for i in range(num_frames):
                origem = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
                frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                frame.blit(folha, (0, 0), origem)
                frames.append(frame)
        else:
            frames = cls._gerar_placeholder(frame_w, frame_h, num_frames, cor_placeholder)

        cls._cache[chave] = frames
        return frames

    @staticmethod
    def _gerar_placeholder(frame_w, frame_h, num_frames, cor):
        """Um retângulo com um traço que se move de frame a frame, só para ficar visível mesmo sem arte real"""
        frames = []
        for i in range(max(1, num_frames)):
            surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            pygame.draw.rect(surf, cor, (2, 2, frame_w - 4, frame_h - 4), border_radius=6)
            pygame.draw.rect(surf, (20, 20, 20), (2, 2, frame_w - 4, frame_h - 4), 2, border_radius=6)
            passo = max(1, num_frames)
            y_traco = 8 + int((frame_h - 16) * (i % passo) / passo)
            pygame.draw.line(surf, (255, 255, 255, 160), (6, y_traco), (frame_w - 6, y_traco), 2)
            frames.append(surf)
        return frames


class Animation:
    """Uma animação: sequência de frames + velocidade (fps) + loop"""

    def __init__(self, frames, fps=10, loop=True):
        self.frames = frames if frames else [pygame.Surface((1, 1), pygame.SRCALPHA)]
        self.fps = fps
        self.loop = loop
        self.tempo_por_frame = 1.0 / fps if fps > 0 else 0.0
        self.reiniciar()

    def reiniciar(self):
        self.tempo_acumulado = 0.0
        self.indice = 0
        #Uma animação de 1 frame sem loop já "termina" imediatamente,
        #senão a entidade ficaria presa nela para sempre.
        self.terminou = len(self.frames) <= 1 and not self.loop

    def atualizar(self, dt):
        if self.terminou or len(self.frames) <= 1 or self.tempo_por_frame <= 0:
            return
        self.tempo_acumulado += dt
        while self.tempo_acumulado >= self.tempo_por_frame:
            self.tempo_acumulado -= self.tempo_por_frame
            self.indice += 1
            if self.indice >= len(self.frames):
                if self.loop:
                    self.indice = 0
                else:
                    self.indice = len(self.frames) - 1
                    self.terminou = True
                    break

    def frame_atual(self):
        return self.frames[self.indice]


class AnimationController:
    """Gerencia várias Animations de uma entidade e a troca entre estados ('idle', 'run', 'attack_sword', ...),"""

    def __init__(self, definicoes, pasta_base, cor_placeholder=(200, 60, 200)):
        self.animacoes = {}
        for nome, info in definicoes.items():
            caminho = os.path.join(pasta_base, info["file"])
            frames = SpriteSheet.carregar_frames(
                caminho, info["frame_w"], info["frame_h"], info["frames"], cor_placeholder
            )
            self.animacoes[nome] = Animation(frames, fps=info["fps"], loop=info["loop"])

        self.estado_atual = None

    def trocar_estado(self, nome, forcar_reinicio=False):
        if nome not in self.animacoes:
            return
        if nome == self.estado_atual and not forcar_reinicio:
            return
        self.estado_atual = nome
        self.animacoes[nome].reiniciar()

    def atualizar(self, dt):
        if self.estado_atual:
            self.animacoes[self.estado_atual].atualizar(dt)

    def animacao_terminou(self):
        if self.estado_atual:
            return self.animacoes[self.estado_atual].terminou
        return True

    def desenhar(self, surface, x, y, facing=1):
        if not self.estado_atual:
            return
        frame = self.animacoes[self.estado_atual].frame_atual()
        if facing < 0:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (x, y))