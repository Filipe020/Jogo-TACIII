"""Ponto de entrada do Shadow Rebirth — jogo de plataforma 2D Run and Gun
/ Roguelite (ver GDD completo)."""

import sys
import pygame

from config import settings
from game.game_manager import GameManager

def main():
    pygame.init()
    pygame.display.set_caption(settings.TITLE)
    # Full HD físico + canvas virtual para manter a interface e os controles.
    from systems.fullscreen import FullscreenCanvas
    video = FullscreenCanvas()
    clock = pygame.time.Clock()
    gerenciador = GameManager(video.canvas)

    rodando = True
    while rodando:
        dt = clock.tick(settings.FPS) / 1000.0
        dt = min(dt, 0.05)  # evita saltos grandes de física após travamentos

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            elif event.type == pygame.VIDEORESIZE:
                video.handle_resize(event.size)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                video.toggle_fullscreen()
            else:
                gerenciador.handle_event(video.map_event(event))

        if gerenciador.sair_solicitado:
            rodando = False
            break
        gerenciador.update(dt)
        gerenciador.draw()
        video.present()
        pygame.display.flip()

    if gerenciador.lan is not None:
        gerenciador.lan.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
