"""Painel de habilidades disponível durante a partida (H ou botão na HUD)."""

import pygame

from config import settings
from systems.progression import UPGRADE_DEFS
from systems.display import font as scaled_font, mouse_pos, sdim, spt, srect, sval


class UpgradeMenu:
    HUD_RECT = pygame.Rect(settings.SCREEN_WIDTH - 204, 16, 188, 42)

    def __init__(self):
        self.chaves = list(UPGRADE_DEFS)
        self.selecionado = 0
        self.font_titulo = None
        self.font_item = None
        self.font_menor = None
        self.font_botao = None
        self.mensagem = ""
        self.mensagem_timer = 0.0

    def abrir(self):
        self.selecionado = 0
        self.mensagem = ""
        self.mensagem_timer = 0.0

    def avisar(self, texto):
        self.mensagem = texto
        self.mensagem_timer = 2.0

    def update(self, dt):
        self.mensagem_timer = max(0.0, self.mensagem_timer - dt)

    def _fontes(self):
        if self.font_titulo is None:
            self.font_titulo = scaled_font(29, bold=True)
            self.font_item = scaled_font(19, bold=True)
            self.font_menor = scaled_font(15)
            self.font_botao = scaled_font(16, bold=True)

    @staticmethod
    def fechar_rect():
        return pygame.Rect(804, 63, 51, 36)

    @staticmethod
    def linha_rect(indice):
        return pygame.Rect(100, 132 + indice * 52, 760, 48)

    @staticmethod
    def melhorar_rect(indice):
        linha = UpgradeMenu.linha_rect(indice)
        return pygame.Rect(710, linha.y + 5, 140, 37)

    def handle_event(self, event):
        """Devolve 'fechar' ou a chave de uma habilidade que se quer comprar."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_h):
                return "fechar"
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selecionado = (self.selecionado - 1) % len(self.chaves)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selecionado = (self.selecionado + 1) % len(self.chaves)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.chaves[self.selecionado]
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.fechar_rect().collidepoint(event.pos):
                return "fechar"
            for idx, chave in enumerate(self.chaves):
                if self.linha_rect(idx).collidepoint(event.pos):
                    self.selecionado = idx
                    return chave
        return None

    def desenhar_botao_hud(self, surface, progression):
        self._fontes()
        destacado = self.HUD_RECT.collidepoint(mouse_pos())
        drect = srect(self.HUD_RECT)
        pygame.draw.rect(
            surface,
            (83, 45, 115) if destacado else (40, 26, 65),
            drect,
            border_radius=sval(8),
        )
        pygame.draw.rect(
            surface,
            (230, 160, 255) if destacado else (144, 99, 185),
            drect,
            sval(2),
            border_radius=sval(8),
        )
        label = self.font_botao.render("HABILIDADES [H]", True, (245, 233, 255))
        surface.blit(label, label.get_rect(center=drect.center))
        pontos = self.font_menor.render(
            f"Pontos: {progression.pontos_disponiveis}", True, (250, 220, 170)
        )
        surface.blit(pontos, pontos.get_rect(topright=(drect.right, drect.bottom + sval(7))))

    def draw(self, surface, progression, multiplayer=False):
        self._fontes()
        mascara = pygame.Surface(sdim(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        mascara.fill((8, 6, 20, 215))
        surface.blit(mascara, (0, 0))

        painel = srect(77, 36, 806, 464)
        pygame.draw.rect(surface, (25, 18, 46), painel, border_radius=sval(13))
        pygame.draw.rect(surface, (135, 91, 179), painel, width=sval(2), border_radius=sval(13))

        titulo = self.font_titulo.render("HABILIDADES", True, (243, 218, 255))
        surface.blit(titulo, spt(104, 59))
        pontos = self.font_item.render(
            f"Pontos: {progression.pontos_disponiveis}", True, (255, 215, 147)
        )
        surface.blit(pontos, spt(510, 69))

        fechar = srect(self.fechar_rect())
        pygame.draw.rect(surface, (74, 36, 78), fechar, border_radius=sval(7))
        pygame.draw.rect(surface, (194, 141, 213), fechar, sval(2), border_radius=sval(7))
        cruz = self.font_item.render("X", True, (250, 230, 255))
        surface.blit(cruz, cruz.get_rect(center=fechar.center))

        mouse = mouse_pos()
        for idx, chave in enumerate(self.chaves):
            info = UPGRADE_DEFS[chave]
            lvl = progression.niveis[chave]
            maximo = lvl >= info["max_nivel"]
            pode = progression.pode_comprar(chave)
            rect = self.linha_rect(idx)
            drect = srect(rect)
            destaque = idx == self.selecionado or rect.collidepoint(mouse)
            cor_linha = (65, 45, 89) if destaque else (36, 29, 61)
            pygame.draw.rect(surface, cor_linha, drect, border_radius=sval(7))
            if destaque:
                pygame.draw.rect(surface, (132, 95, 165), drect, sval(1), border_radius=sval(7))

            nome = self.font_item.render(
                f"{info['nome']}  Nv {lvl}/{info['max_nivel']}", True, (241, 225, 255)
            )
            desc = self.font_menor.render(info["descricao"], True, (181, 176, 202))
            surface.blit(nome, (drect.x + sval(13), drect.y + sval(4)))
            surface.blit(desc, (drect.x + sval(13), drect.y + sval(27)))

            button = srect(self.melhorar_rect(idx))
            button_cor = (80, 53, 114) if pode else (49, 45, 61)
            pygame.draw.rect(surface, button_cor, button, border_radius=sval(6))
            pygame.draw.rect(
                surface,
                (205, 144, 246) if pode else (99, 95, 109),
                button,
                sval(1),
                border_radius=sval(6),
            )
            label = (
                "NÍVEL MÁX."
                if maximo
                else f"EVOLUIR ({progression.custo_proximo_nivel(chave)})"
            )
            txt = self.font_botao.render(
                label, True, (247, 232, 255) if pode else (144, 139, 154)
            )
            surface.blit(txt, txt.get_rect(center=button.center))

        instrucoes = (
            "LAN: pontos e níveis compartilhados | H / ESC para voltar"
            if multiplayer
            else "↑ / ↓: selecionar  ENTER: evoluir  H / ESC: voltar"
        )
        texto = self.font_menor.render(instrucoes, True, (200, 190, 220))
        surface.blit(texto, texto.get_rect(center=spt(settings.SCREEN_WIDTH // 2, 466)))
        if self.mensagem_timer > 0 and self.mensagem:
            texto = self.font_menor.render(self.mensagem, True, (255, 219, 159))
            surface.blit(texto, texto.get_rect(center=spt(settings.SCREEN_WIDTH // 2, 116)))