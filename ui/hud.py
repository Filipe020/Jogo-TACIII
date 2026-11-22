"""HUD exibido durante a Run"""

import os
import pygame
from config import settings
from systems.icons import IconLoader
from systems.display import font, spt, srect, sval

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
        self.fonte = font(18, bold=True)
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
        x, y_vida = 20, 18
        surface.blit(self.icone_vida, spt(x, y_vida))
        largura_barra = 190
        bx, by = x + TAMANHO_ICONE + 8, y_vida + 2
        pct = max(0, player.health / player.max_health)
        pygame.draw.rect(surface, settings.COLOR_HP_BG, srect(bx, by, largura_barra, 18))
        pygame.draw.rect(surface, settings.COLOR_HP, srect(bx, by, int(largura_barra * pct), 18))
        pygame.draw.rect(surface, (20, 20, 20), srect(bx, by, largura_barra, 18), sval(2))
        texto_vida = self.fonte.render(f"{int(player.health)}/{int(player.max_health)}", True, settings.COLOR_TEXT)
        surface.blit(texto_vida, spt(bx + largura_barra + 10, by - 1))

        y_shuriken = y_vida + 32
        surface.blit(self.icone_shuriken, spt(x, y_shuriken))
        texto_shuriken = self.fonte.render(f"{player.shurikens}/{player.shurikens_max}", True, settings.COLOR_SHURIKEN)
        surface.blit(texto_shuriken, spt(x + TAMANHO_ICONE + 8, y_shuriken + 3))

        y_kills = y_shuriken + 30
        surface.blit(self.icone_kills, spt(x, y_kills))
        rotulo_kills = (
            f"{run_state.inimigos_derrotados}/{run_state.meta_inimigos}"
            if run_state.fase_atual == 1
            else f"{run_state.inimigos_derrotados} (FASE FINAL)"
        )
        texto_kills = self.fonte.render(rotulo_kills, True, settings.COLOR_TEXT)
        surface.blit(texto_kills, spt(x + TAMANHO_ICONE + 8, y_kills + 3))
