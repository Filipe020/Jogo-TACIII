"""HUD exibido durante a Run: vida, shurikens e contador de inimigos
derrotados (ver GDD seção 18)."""

import pygame

from config import settings


class HUD:
    def __init__(self):
        self.fonte = None

    def _fonte(self):
        if not self.fonte:
            self.fonte = pygame.font.SysFont("consolas", 18, bold=True)

    def draw(self, surface, player, run_state):
        self._fonte()

        largura_barra = 220
        x, y = 20, 20
        pct = max(0, player.health / player.max_health)
        pygame.draw.rect(surface, settings.COLOR_HP_BG, (x, y, largura_barra, 18))
        pygame.draw.rect(surface, settings.COLOR_HP, (x, y, int(largura_barra * pct), 18))
        pygame.draw.rect(surface, (20, 20, 20), (x, y, largura_barra, 18), 2)
        texto_vida = self.fonte.render(
            f"{int(player.health)}/{int(player.max_health)}", True, settings.COLOR_TEXT
        )
        surface.blit(texto_vida, (x + largura_barra + 10, y - 1))

        y2 = y + 30
        texto_shuriken = self.fonte.render(
            f"Shurikens: {player.shurikens}/{player.shurikens_max}", True, settings.COLOR_SHURIKEN
        )
        surface.blit(texto_shuriken, (x, y2))

        y3 = y2 + 26
        texto_kills = self.fonte.render(
            f"Inimigos derrotados: {run_state.inimigos_derrotados}", True, settings.COLOR_TEXT
        )
        surface.blit(texto_kills, (x, y3))
