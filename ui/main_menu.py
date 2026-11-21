"""Menu principal com fundo ilustrado e botões interativos."""

import os
import pygame
from config import settings


class MainMenu:
    def __init__(self):
        self.fonte_titulo = pygame.font.SysFont("consolas", 58, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("consolas", 18)
        self.fonte_botao = pygame.font.SysFont("consolas", 22, bold=True)
        self.fonte_pequena = pygame.font.SysFont("consolas", 16)
        self.background = self._carregar_fundo()
        self.tela = "principal"
        self.mensagem = ""
        self.mensagem_timer = 0.0
        self.botoes = []

    def _carregar_fundo(self):
        try:
            imagem = pygame.image.load(settings.MENU_BACKGROUND).convert()
            return pygame.transform.smoothscale(imagem, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        except (pygame.error, OSError):
            return None

    def avisar(self, texto):
        self.mensagem = texto
        self.mensagem_timer = 3.0

    def handle_event(self, event, tem_save):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.tela != "principal":
                self.tela = "principal"
                return None
        if self.tela == "configuracoes":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.avisar("Controles: A/D mover | W/Espaço pular | Mouse atacar")
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for nome, rect in self.botoes:
                if rect.collidepoint(event.pos):
                    if nome == "Configurações":
                        self.tela = "configuracoes"
                        return None
                    if nome == "Continuar" and not tem_save:
                        self.avisar("Nenhum progresso salvo. Escolha Novo Jogo.")
                        return None
                    if nome == "Multiplayer":
                        self.avisar("Multiplayer: funcionalidade em desenvolvimento.")
                        return None
                    if nome == "Editor de Fases":
                        self.avisar("O módulo do editor não está presente neste arquivo ZIP.")
                        return None
                    return "novo_jogo" if nome == "Novo Jogo" else "continuar"
        return None

    def update(self, dt):
        if self.mensagem_timer > 0:
            self.mensagem_timer = max(0, self.mensagem_timer - dt)

    def _desenhar_botao(self, surface, nome, y, habilitado=True):
        rect = pygame.Rect(0, 0, 300, 42)
        rect.center = (settings.SCREEN_WIDTH // 2, y)
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)
        cor = (70, 42, 100) if hover and habilitado else (30, 22, 52)
        borda = (224, 151, 255) if hover and habilitado else (135, 91, 177)
        if not habilitado:
            cor, borda = (28, 25, 37), (80, 75, 90)
        pygame.draw.rect(surface, cor, rect, border_radius=8)
        pygame.draw.rect(surface, borda, rect, width=2, border_radius=8)
        texto = self.fonte_botao.render(nome, True, (245, 235, 255) if habilitado else (130, 125, 140))
        surface.blit(texto, texto.get_rect(center=rect.center))
        self.botoes.append((nome, rect))

    def draw(self, surface, tem_save=True):
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((18, 14, 35))
        # Sombra suave para garantir leitura do menu sobre a arte.
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((7, 5, 22, 105))
        surface.blit(overlay, (0, 0))

        self.botoes = []
        if self.tela == "configuracoes":
            titulo = self.fonte_titulo.render("CONFIGURAÇÕES", True, (246, 220, 255))
            surface.blit(titulo, titulo.get_rect(center=(480, 150)))
            linhas = ["CONTROLES", "A / D  -  Movimentar", "W / ESPAÇO  -  Pular", "Botão esquerdo  -  Espada", "Botão direito  -  Shuriken", "ESC  -  Voltar ao menu"]
            for i, linha in enumerate(linhas):
                fonte = self.fonte_botao if i == 0 else self.fonte_subtitulo
                texto = fonte.render(linha, True, (245, 235, 255))
                surface.blit(texto, texto.get_rect(center=(480, 235 + i * 38)))
            return

        titulo = self.fonte_titulo.render("SHADOW REBIRTH", True, (255, 224, 255))
        surface.blit(titulo, titulo.get_rect(center=(480, 105)))
        subtitulo = self.fonte_subtitulo.render("UM NINJA. UMA LÂMINA. RUNS INFINITAS.", True, (235, 220, 255))
        surface.blit(subtitulo, subtitulo.get_rect(center=(480, 151)))

        self._desenhar_botao(surface, "Novo Jogo", 230)
        self._desenhar_botao(surface, "Continuar", 280, tem_save)
        self._desenhar_botao(surface, "Multiplayer", 330)
        self._desenhar_botao(surface, "Editor de Fases", 380)
        self._desenhar_botao(surface, "Configurações", 430)
        if self.mensagem_timer > 0 and self.mensagem:
            texto = self.fonte_pequena.render(self.mensagem, True, (255, 230, 170))
            fundo = pygame.Surface((texto.get_width() + 28, 34), pygame.SRCALPHA)
            fundo.fill((10, 8, 20, 210))
            surface.blit(fundo, fundo.get_rect(center=(480, 495)))
            surface.blit(texto, texto.get_rect(center=(480, 495)))
