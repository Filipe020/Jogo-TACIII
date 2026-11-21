"""Ponto de entrada do Shadow Rebirth — jogo de plataforma 2D Run and Gun / Roguelite"""

import sys

import pygame

from config import settings
from game.game_manager import GameManager

def main():
    pygame.init()
    pygame.display.set_caption(settings.TITLE)
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
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

        gerenciador.update(dt)
        gerenciador.draw()
        pygame.display.flip()

    if gerenciador.lan is not None:
        gerenciador.lan.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
