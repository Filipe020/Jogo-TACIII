"""Arena da Fase Final — Santuário do Chefe com cenário próprio."""

from levels.rooms import plataforma, gerar_chao

LARGURA_ARENA = 1600
CHAO_Y = 524


def mapa_fase_final():
    plataformas = [
        gerar_chao(0, LARGURA_ARENA, CHAO_Y, altura=16),
        plataforma(160, 435, 210),
        plataforma(470, 355, 220),
        plataforma(910, 355, 220),
        plataforma(1230, 435, 210),
    ]
    return {
        "nome": "Fase Final - Santuário Carmesim",
        "largura": LARGURA_ARENA,
        "spawn_jogador": [120, CHAO_Y - 60],
        "plataformas": [list(rect) for rect in plataformas],
        "inimigos": [],
        "spawn_automatico": False,
    }
