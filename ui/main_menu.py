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
        self.ip_servidor = "127.0.0.1"
        self.ip_ativo = False
        self.som_ativo = True  # O GameManager sincroniza com o AudioManager.

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
        if event.type == pygame.KEYDOWN:
            if self.tela == "configuracoes" and event.key == pygame.K_m:
                return "alternar_som"
            if event.key == pygame.K_ESCAPE and self.tela != "principal":
                self.tela = "principal"
                self.ip_ativo = False
                return None
            if self.tela == "multiplayer":
                if event.key == pygame.K_RETURN:
                    return "lan_join:" + self.ip_servidor.strip()
                if self.ip_ativo:
                    if event.key == pygame.K_BACKSPACE:
                        self.ip_servidor = self.ip_servidor[:-1]
                    elif event.unicode and len(self.ip_servidor) < 60:
                        if all(c.isascii() and (c.isalnum() or c in ".-_") for c in event.unicode):
                            self.ip_servidor += event.unicode
                return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.tela == "multiplayer":
                self.ip_ativo = pygame.Rect(280, 213, 400, 46).collidepoint(event.pos)
            for nome, rect in self.botoes:
                if not rect.collidepoint(event.pos):
                    continue
                if nome == "Voltar":
                    self.tela = "principal"
                    self.ip_ativo = False
                    return None
                if self.tela == "configuracoes":
                    if nome.startswith("Sons:"):
                        return "alternar_som"
                    return None
                if self.tela == "multiplayer":
                    if nome == "Criar sala":
                        return "lan_host"
                    if nome == "Entrar na sala":
                        return "lan_join:" + self.ip_servidor.strip()
                    return None
                if nome == "Sair do Jogo":
                    return "sair"
                if nome == "Configurações":
                    self.tela = "configuracoes"
                    return None
                if nome == "Multiplayer":
                    self.tela = "multiplayer"
                    return None
                if nome == "Continuar" and not tem_save:
                    self.avisar("Nenhum progresso salvo. Escolha Novo Jogo.")
                    return None
                if nome == "Editor de Fases":
                    return "editor"
                if nome in ("Novo Jogo", "Continuar"):
                    return "novo_jogo" if nome == "Novo Jogo" else "continuar"
        return None

    def update(self, dt):
        if self.mensagem_timer > 0:
            self.mensagem_timer = max(0, self.mensagem_timer - dt)

    def _desenhar_botao(self, surface, nome, y, habilitado=True):
        rect = pygame.Rect(0, 0, 300, 42)
        rect.center = (settings.SCREEN_WIDTH // 2, y)
        mouse = settings.posicao_mouse_logica()
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
            surface.blit(titulo, titulo.get_rect(center=(480, 112)))
            linhas = ["CONTROLES", "A / D  -  Movimentar", "W / ESPAÇO  -  Pular", "Botão esquerdo  -  Espada", "Botão direito  -  Shuriken", "H - Habilidades durante a partida"]
            for i, linha in enumerate(linhas):
                fonte = self.fonte_botao if i == 0 else self.fonte_subtitulo
                texto = fonte.render(linha, True, (245, 235, 255))
                surface.blit(texto, texto.get_rect(center=(480, 180 + i * 35)))
            self._desenhar_botao(
                surface, "Sons: LIGADOS" if self.som_ativo else "Sons: DESLIGADOS", 415
            )
            self._desenhar_botao(surface, "Voltar", 474)
            return

        if self.tela == "multiplayer":
            titulo = self.fonte_titulo.render("MULTIPLAYER LAN", True, (255, 224, 255))
            surface.blit(titulo, titulo.get_rect(center=(480, 96)))
            subtitulo = self.fonte_subtitulo.render("2 jogadores na mesma rede Wi-Fi ou cabo", True, (235, 220, 255))
            surface.blit(subtitulo, subtitulo.get_rect(center=(480, 151)))
            texto = self.fonte_subtitulo.render("IP do computador que vai criar a sala:", True, (240, 225, 250))
            surface.blit(texto, texto.get_rect(center=(480, 194)))
            campo = pygame.Rect(280, 213, 400, 46)
            pygame.draw.rect(surface, (25, 20, 43), campo, border_radius=8)
            pygame.draw.rect(surface, (236, 159, 255) if self.ip_ativo else (130, 95, 168), campo, 2, border_radius=8)
            ip = self.fonte_botao.render(self.ip_servidor, True, (245, 235, 255))
            surface.blit(ip, (campo.x + 14, campo.y + 10))
            self._desenhar_botao(surface, "Criar sala", 315)
            self._desenhar_botao(surface, "Entrar na sala", 368)
            self._desenhar_botao(surface, "Voltar", 433)
            self._desenhar_mensagem(surface)
            return

        titulo = self.fonte_titulo.render("SHADOW REBIRTH", True, (255, 224, 255))
        surface.blit(titulo, titulo.get_rect(center=(480, 105)))
        subtitulo = self.fonte_subtitulo.render("UM NINJA. UMA LÂMINA. RUNS INFINITAS.", True, (235, 220, 255))
        surface.blit(subtitulo, subtitulo.get_rect(center=(480, 151)))

        self._desenhar_botao(surface, "Novo Jogo", 208)
        self._desenhar_botao(surface, "Continuar", 256, tem_save)
        self._desenhar_botao(surface, "Multiplayer", 304)
        self._desenhar_botao(surface, "Editor de Fases", 352)
        self._desenhar_botao(surface, "Configurações", 400)
        self._desenhar_botao(surface, "Sair do Jogo", 448)
        self._desenhar_mensagem(surface)

    def _desenhar_mensagem(self, surface):
        if self.mensagem_timer > 0 and self.mensagem:
            texto = self.fonte_pequena.render(self.mensagem, True, (255, 230, 170))
            fundo = pygame.Surface((texto.get_width() + 28, 34), pygame.SRCALPHA)
            fundo.fill((10, 8, 20, 210))
            surface.blit(fundo, fundo.get_rect(center=(480, 495)))
            surface.blit(texto, texto.get_rect(center=(480, 495)))
