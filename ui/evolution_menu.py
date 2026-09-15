"""Tela da Sala de Evolução — o jogador gasta os pontos obtidos na Run
para comprar melhorias permanentes (ver GDD seções 14 e 15)."""

import pygame

from config import settings
from systems.progression import UPGRADE_DEFS


class EvolutionMenu:
    def __init__(self, progression):
        self.progression = progression
        self.opcoes = list(UPGRADE_DEFS.keys())
        self.selecionado = 0
        self.confirmar_iniciar_run = False
        self.fonte_titulo = None
        self.fonte_texto = None
        self.fonte_pequena = None

    def atualizar_opcoes(self):
        self.selecionado = 0
        self.confirmar_iniciar_run = False

    def _fontes(self):
        if not self.fonte_titulo:
            self.fonte_titulo = pygame.font.SysFont("consolas", 32, bold=True)
            self.fonte_texto = pygame.font.SysFont("consolas", 20)
            self.fonte_pequena = pygame.font.SysFont("consolas", 16)

    def handle_event(self, event, audio):
        total_itens = len(self.opcoes) + 1  # +1 para "Iniciar nova Run"

        if event.key == pygame.K_w:
            self.selecionado = (self.selecionado - 1) % total_itens
            audio.play("menu")
        elif event.key == pygame.K_s:
            self.selecionado = (self.selecionado + 1) % total_itens
            audio.play("menu")
        elif event.key == pygame.K_RETURN:
            if self.selecionado == len(self.opcoes):
                self.confirmar_iniciar_run = True
            else:
                chave = self.opcoes[self.selecionado]
                if self.progression.comprar(chave):
                    audio.play("upgrade")

    def draw(self, surface, progression, run_state):
        self._fontes()
        surface.fill(settings.COLOR_BG)

        titulo = self.fonte_titulo.render("SALA DE EVOLUÇÃO", True, settings.COLOR_ACCENT)
        surface.blit(titulo, titulo.get_rect(center=(settings.SCREEN_WIDTH // 2, 55)))

        pontos = self.fonte_texto.render(
            f"Inimigos derrotados disponíveis: {progression.pontos_disponiveis}",
            True, settings.COLOR_TEXT,
        )
        surface.blit(pontos, pontos.get_rect(center=(settings.SCREEN_WIDTH // 2, 92)))

        y = 135
        for i, chave in enumerate(self.opcoes):
            info = UPGRADE_DEFS[chave]
            nivel = progression.niveis[chave]
            custo = progression.custo_proximo_nivel(chave)
            no_maximo = nivel >= info["max_nivel"]

            cor = settings.COLOR_ACCENT if i == self.selecionado else settings.COLOR_TEXT
            prefixo = "> " if i == self.selecionado else "  "

            status = "MÁXIMO" if no_maximo else f"custo: {custo}"
            linha = f"{prefixo}{info['nome']} (nível {nivel}/{info['max_nivel']}) — {status}"
            texto = self.fonte_texto.render(linha, True, cor)
            surface.blit(texto, (80, y))

            desc = self.fonte_pequena.render(info["descricao"], True, (170, 170, 180))
            surface.blit(desc, (100, y + 24))
            y += 52

        cor_final = settings.COLOR_ACCENT if self.selecionado == len(self.opcoes) else settings.COLOR_TEXT
        prefixo_final = "> " if self.selecionado == len(self.opcoes) else "  "
        final = self.fonte_texto.render(f"{prefixo_final}Iniciar nova Run", True, cor_final)
        surface.blit(final, (80, y + 6))

        ajuda = self.fonte_pequena.render(
            "W/S — navegar   ENTER — comprar / confirmar", True, (150, 150, 160)
        )
        surface.blit(ajuda, (80, settings.SCREEN_HEIGHT - 36))
