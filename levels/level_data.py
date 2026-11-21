"""Leitura, validação e persistência dos mapas criados no editor.

Os arquivos ficam em levels/custom_level_01.json, ...02.json, ...03.json.
Não é necessário alterar código Python para editar uma fase.
"""

import json
import os
from copy import deepcopy

from config import settings
from levels import level_01

TIPOS_INIMIGOS = ("basico", "rapido", "resistente", "distancia")
SLOTS = (1, 2, 3)
LARGURA_MIN = settings.SCREEN_WIDTH
LARGURA_MAX = 12000


def caminho_slot(slot):
    if slot not in SLOTS:
        raise ValueError("Slot de fase inválido")
    return os.path.join(settings.BASE_DIR, "levels", f"custom_level_{slot:02}.json")


def mapa_padrao():
    return {
        "nome": "Templo em Ruínas",
        "largura": level_01.LARGURA_NIVEL,
        "spawn_jogador": list(level_01.spawn_inicial_jogador()),
        "plataformas": [list(rect) for rect in level_01.construir_plataformas()],
        "inimigos": [],
        "spawn_automatico": True,
    }


def mapa_novo():
    return {
        "nome": "Nova fase",
        "largura": 3600,
        "spawn_jogador": [60, 400],
        "plataformas": [[0, 460, 3600, 40]],
        "inimigos": [],
        "spawn_automatico": True,
    }


def normalizar_mapa(mapa):
    """Valida JSON externo e converte os dados em tipos seguros para o Pygame."""
    if not isinstance(mapa, dict):
        raise ValueError("O mapa precisa ser um objeto JSON")
    largura = int(mapa["largura"])
    if not LARGURA_MIN <= largura <= LARGURA_MAX:
        raise ValueError(f"Largura precisa estar entre {LARGURA_MIN} e {LARGURA_MAX}")

    spawn = mapa["spawn_jogador"]
    if not isinstance(spawn, (list, tuple)) or len(spawn) != 2:
        raise ValueError("Spawn do jogador inválido")
    sx, sy = (int(value) for value in spawn)
    if not 0 <= sx <= largura - 28 or not 0 <= sy <= settings.SCREEN_HEIGHT - 44:
        raise ValueError("Spawn do jogador fora dos limites")

    raw_plataformas = mapa["plataformas"]
    if not isinstance(raw_plataformas, list) or len(raw_plataformas) > 500:
        raise ValueError("Quantidade de plataformas inválida (máximo 500)")
    plataformas = []
    for p in raw_plataformas:
        if not isinstance(p, (list, tuple)) or len(p) != 4:
            raise ValueError("Plataforma deve ter x, y, largura e altura")
        x, y, w, h = (int(value) for value in p)
        if not (0 <= x < largura and 0 <= y < settings.SCREEN_HEIGHT and
                0 < w <= largura - x and 0 < h <= settings.SCREEN_HEIGHT - y):
            raise ValueError(f"Plataforma fora dos limites: {p}")
        plataformas.append([x, y, w, h])

    raw_inimigos = mapa.get("inimigos", [])
    if not isinstance(raw_inimigos, list) or len(raw_inimigos) > 200:
        raise ValueError("Quantidade de inimigos inválida (máximo 200)")
    inimigos = []
    for e in raw_inimigos:
        if not isinstance(e, dict):
            raise ValueError("Inimigo inválido")
        tipo, x, y = e.get("tipo"), int(e["x"]), int(e["y"])
        if tipo not in TIPOS_INIMIGOS or not (0 <= x < largura and 0 <= y < settings.SCREEN_HEIGHT):
            raise ValueError(f"Posição ou tipo de inimigo inválido: {e}")
        inimigos.append({"tipo": tipo, "x": x, "y": y})

    return {
        "nome": str(mapa.get("nome", "Fase personalizada"))[:60],
        "largura": largura,
        "spawn_jogador": [sx, sy],
        "plataformas": plataformas,
        "inimigos": inimigos,
        "spawn_automatico": bool(mapa.get("spawn_automatico", True)),
    }


def carregar_slot(slot):
    caminho = caminho_slot(slot)
    if not os.path.exists(caminho):
        return None
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return normalizar_mapa(json.load(arquivo))


def salvar_slot(slot, mapa):
    """Escreve o mapa em arquivo temporário e substitui o anterior atomicamente."""
    conteudo = normalizar_mapa(deepcopy(mapa))
    caminho = caminho_slot(slot)
    temporario = caminho + ".tmp"
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, indent=2, ensure_ascii=False)
        arquivo.write("\n")
    os.replace(temporario, caminho)
    return caminho
