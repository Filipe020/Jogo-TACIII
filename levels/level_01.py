"""Nível inicial — templo em ruínas com plataformas em diferentes alturas."""

from levels.rooms import plataforma, gerar_chao

LARGURA_NIVEL = 3600
CHAO_Y = 460

def construir_plataformas():
    return [
        gerar_chao(0, LARGURA_NIVEL, CHAO_Y),
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
        plataforma(3050, 380, 220),
    ]


def limites_nivel():
    return (0, LARGURA_NIVEL)


def spawn_inicial_jogador():
    return (60, CHAO_Y - 100)
