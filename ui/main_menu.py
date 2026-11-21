"""Menu inicial do jogo."""

import pygame

from config import settings


class MainMenu:
    def __init__(self):
        self.fonte_titulo = None
        self.fonte_texto = None

    def _fontes(self):
        if not self.fonte_titulo:
            self.fonte_titulo = pygame.font.SysFont("consolas", 54, bold=True)
            self.fonte_texto = pygame.font.SysFont("consolas", 20)

    def draw(self, surface):
        self._fontes()
        surface.fill(settings.COLOR_BG)

        titulo = self.fonte_titulo.render("SHADOW REBIRTH", True, settings.COLOR_ACCENT)
        surface.blit(titulo, titulo.get_rect(center=(settings.SCREEN_WIDTH // 2, 170)))

        subtitulo = self.fonte_texto.render(
            "Um ninja. Uma lâmina. Runs infinitas.", True, settings.COLOR_TEXT
        )
        surface.blit(subtitulo, subtitulo.get_rect(center=(settings.SCREEN_WIDTH // 2, 230)))

        linhas = [
            "ENTER — Jogar fase salva",
            "E — Abrir Editor de Fases",
            "A / D — Mover      W / ESPAÇO — Pular",
            "Clique esquerdo — Espada      Clique direito — Shuriken      ESC — Pausar",
        ]
        y = 308
        for linha in linhas:
            texto = self.fonte_texto.render(linha, True, settings.COLOR_TEXT)
            surface.blit(texto, texto.get_rect(center=(settings.SCREEN_WIDTH // 2, y)))
            y += 36
