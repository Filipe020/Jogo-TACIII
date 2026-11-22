"""Nível inicial — templo em ruínas com plataformas em diferentes alturas."""

from levels.rooms import plataforma, gerar_chao

LARGURA_NIVEL = 3600
CHAO_Y = 528

def construir_plataformas():
    return [
        gerar_chao(0, LARGURA_NIVEL, CHAO_Y, altura=12),
        plataforma(260, 430, 160),
        plataforma(520, 370, 140),
        plataforma(760, 445, 180),
        plataforma(1050, 330, 120),
        plataforma(1300, 410, 200),
        plataforma(1650, 370, 140),
        plataforma(1900, 445, 220),
        plataforma(2200, 330, 140),
        plataforma(2450, 410, 180),
        plataforma(2750, 370, 160),
        plataforma(3050, 445, 220),
    ]


def limites_nivel():
    return (0, LARGURA_NIVEL)


def spawn_inicial_jogador():
    return (60, CHAO_Y - 60)
