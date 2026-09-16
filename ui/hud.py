"""HUD exibido durante a Run: ícone + barra de vida, ícone + quantidade de shurikens, ícone + contador de inimigos derrotados"""

import os

import pygame

from config import settings
from systems.icons import IconLoader

PASTA_ICONES = os.path.join(settings.BASE_DIR, "assets", "sprites", "ui")
TAMANHO_ICONE = 22


class HUD:
    def __init__(self):
        self.fonte = None
        self.icone_vida = None
        self.icone_shuriken = None
        self.icone_kills = None

    def _preparar(self):
        if self.fonte:
            return
        self.fonte = pygame.font.SysFont("consolas", 18, bold=True)
        self.icone_vida = IconLoader.carregar(
            os.path.join(PASTA_ICONES, "heart.png"), TAMANHO_ICONE, settings.COLOR_HP, "coracao"
        )
        self.icone_shuriken = IconLoader.carregar(
            os.path.join(PASTA_ICONES, "shuriken_icon.png"), TAMANHO_ICONE, settings.COLOR_SHURIKEN, "diamante"
        )
        self.icone_kills = IconLoader.carregar(
            os.path.join(PASTA_ICONES, "skull.png"), TAMANHO_ICONE, settings.COLOR_ACCENT, "estrela"
        )

    def draw(self, surface, player, run_state):
        self._preparar()

        x = 20
        y_vida = 18

        # --- Vida: ícone + barra ---
        surface.blit(self.icone_vida, (x, y_vida))
        largura_barra = 190
        bx = x + TAMANHO_ICONE + 8
        by = y_vida + 2
        pct = max(0, player.health / player.max_health)
        pygame.draw.rect(surface, settings.COLOR_HP_BG, (bx, by, largura_barra, 18))
        pygame.draw.rect(surface, settings.COLOR_HP, (bx, by, int(largura_barra * pct), 18))
        pygame.draw.rect(surface, (20, 20, 20), (bx, by, largura_barra, 18), 2)
        texto_vida = self.fonte.render(
            f"{int(player.health)}/{int(player.max_health)}", True, settings.COLOR_TEXT
        )
        surface.blit(texto_vida, (bx + largura_barra + 10, by - 1))

        # --- Arma (shurikens): ícone + quantidade ---
        y_shuriken = y_vida + 32
        surface.blit(self.icone_shuriken, (x, y_shuriken))
        texto_shuriken = self.fonte.render(
            f"{player.shurikens}/{player.shurikens_max}", True, settings.COLOR_SHURIKEN
        )
        surface.blit(texto_shuriken, (x + TAMANHO_ICONE + 8, y_shuriken + 3))

        # --- Pontos (inimigos derrotados): ícone + contador ---
        y_kills = y_shuriken + 30
        surface.blit(self.icone_kills, (x, y_kills))
        texto_kills = self.fonte.render(
            f"{run_state.inimigos_derrotados}", True, settings.COLOR_TEXT
        )
        surface.blit(texto_kills, (x + TAMANHO_ICONE + 8, y_kills + 3))
