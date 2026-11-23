"""Nível inicial — templo em ruínas com plataformas em diferentes alturas."""

from levels.rooms import plataforma
from config import settings

LARGURA_NIVEL = 3600
CHAO_Y = settings.GROUND_Y  # mesma altura do chão físico invisível

def construir_plataformas():
    return [
        plataforma(260, 360, 160),
        plataforma(520, 300, 140),
        plataforma(760, 380, 180),
        plataforma(1050, 260, 120),
        plataforma(1300, 340, 200),
        plataforma(1650, 300, 140),
        plataforma(1900, 380, 220),
        plataforma(2200, 260, 140),
        plataforma(2450, 340, 180),
        plataforma(2750, 300, 160),
        plataforma(3020, 380, 180),
        plataforma(3260, 310, 150),
        plataforma(3450, 250, 120),
    ]

def limites_nivel():
    return (0, LARGURA_NIVEL)


def spawn_inicial_jogador():
    return (60, CHAO_Y - 44)  # inicia com os pés no terreno da arte
