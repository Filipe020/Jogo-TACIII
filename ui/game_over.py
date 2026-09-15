"""Overlay breve exibido no momento da morte, antes de ir para a Sala de
Evolução (ver GDD seção 17 - Sistema de Morte)."""

import pygame

from config import settings


class GameOverScreen:
    def __init__(self):
        self.fonte_titulo = None
        self.fonte_texto = None

    def _fontes(self):
        if not self.fonte_titulo:
            self.fonte_titulo = pygame.font.SysFont("consolas", 44, bold=True)
            self.fonte_texto = pygame.font.SysFont("consolas", 20)

    def draw(self, surface, run_state):
        self._fontes()
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        titulo = self.fonte_titulo.render("Você caiu...", True, settings.COLOR_HP)
        surface.blit(
            titulo, titulo.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 30))
        )

        texto = self.fonte_texto.render(
            f"Inimigos derrotados nesta Run: {run_state.inimigos_derrotados}", True, settings.COLOR_TEXT
        )
        surface.blit(
            texto, texto.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 20))
        )
