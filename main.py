"""Ponto de entrada do Shadow Rebirth — jogo de plataforma 2D Run and Gun
/ Roguelite (ver GDD completo)."""

import sys

import pygame

from config import settings
from game.game_manager import GameManager


def criar_janela(fullscreen=None):
    if fullscreen is None:
        fullscreen = bool(getattr(settings, "FULLSCREEN", True))
    flags = (pygame.FULLSCREEN | pygame.SCALED) if fullscreen else pygame.SCALED
    try:
        return pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), flags)
    except pygame.error:
        fallback_flags = pygame.FULLSCREEN if fullscreen else 0
        return pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), fallback_flags)


def main():
    pygame.init()
    pygame.display.set_caption(settings.TITLE)
    screen = criar_janela()
    clock = pygame.time.Clock()

    gerenciador = GameManager(screen)

    rodando = True
    while rodando:
        dt = clock.tick(settings.FPS) / 1000.0
        dt = min(dt, 0.05)  # evita saltos grandes de física após travamentos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            else:
                gerenciador.handle_event(event)

        if gerenciador.sair_solicitado:
            rodando = False
            break
        gerenciador.update(dt)
        gerenciador.draw()
        pygame.display.flip()

    if gerenciador.lan is not None:
        gerenciador.lan.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()