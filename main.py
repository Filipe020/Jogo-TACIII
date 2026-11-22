"""Ponto de entrada do Shadow Rebirth — jogo de plataforma 2D Run and Gun
/ Roguelite (ver GDD completo)."""

import sys

import pygame

from config import settings
from game.game_manager import GameManager
from systems.display import scale_event


def main():
    pygame.init()
    pygame.display.set_caption(settings.TITLE)
    flags = pygame.FULLSCREEN | pygame.SCALED
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), flags)
    clock = pygame.time.Clock()

    gerenciador = GameManager(screen)

    rodando = True
    while rodando:
        dt = clock.tick(settings.FPS) / 1000.0
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            else:
                gerenciador.handle_event(scale_event(event))

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
