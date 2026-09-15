"""Funções auxiliares para montar plataformas que compõem um nível
(ver GDD seção 12)."""

import pygame


def plataforma(x, y, width, height=24):
    return pygame.Rect(x, y, width, height)


def gerar_chao(x_inicio, x_fim, y, altura=40):
    return plataforma(x_inicio, y, x_fim - x_inicio, altura)
