"""Configurações globais do Shadow Rebirth"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#---Janela---

'''Deixar no projeto final em FullScream'''

# Resolução virtual mantém física, sprites e menus compatíveis. O monitor
# renderiza essa cena em Full HD (ou na maior resolução disponível).
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
RENDER_SCALE = 2
FULLHD_WIDTH = SCREEN_WIDTH * RENDER_SCALE
FULLHD_HEIGHT = SCREEN_HEIGHT * RENDER_SCALE
FULLSCREEN = True
DISPLAY_VIEWPORT = (0, 0, FULLHD_WIDTH, FULLHD_HEIGHT)


def posicao_mouse_logica():
    """Converte cursor físico para a resolução virtual usada por todos os menus."""
    from systems.display import mouse_pos
    return mouse_pos()


FPS = 60
TITLE = "Shadow Rebirth"

#---Física---
GRAVITY = 1800.0          #Gravidade
MAX_FALL_SPEED = 1200.0   #Velocidade da queda
MOVE_SPEED = 260.0        #Velocidade do Personagem
JUMP_POWER = 860.0        # Impulso suficiente para alcançar as primeiras plataformas (altura ~205 px)

# Chão invisível alinhado à trilha de pedras na imagem de fundo.
# O sprite do jogador tem cerca de 4 px de transparência abaixo dos pés.
GROUND_Y = 486

#---Paleta de cores---
COLOR_BG = (18, 14, 28)
COLOR_BG_FAR = (30, 24, 44)
COLOR_PLATFORM = (72, 54, 46)
COLOR_PLATFORM_TOP = (110, 82, 60)
COLOR_PLAYER = (210, 210, 220)
COLOR_PLAYER_OUTLINE = (30, 30, 40)
COLOR_SWORD = (230, 230, 160)
COLOR_SHURIKEN = (180, 220, 255)
COLOR_HP = (200, 40, 50)
COLOR_HP_BG = (60, 20, 24)
COLOR_TEXT = (235, 235, 235)
COLOR_ACCENT = (180, 60, 200)

ENEMY_COLORS = {
    "basico": (150, 60, 60),
    "rapido": (230, 170, 60),
    "resistente": (90, 90, 150),
    "distancia": (90, 170, 110),
    "chefe": (141, 57, 195),
}

#---Controles---
# A / D              -> mover
# W ou ESPAÇO        -> pular
# Clique esquerdo    -> espada
# Clique direito     -> shuriken
# H                  -> habilidades durante a partida
# ESC                -> pausar / abrir menu
# Enter              -> confirmar seleção

#---Save---
SAVE_FILE = os.path.join(BASE_DIR, "savegame.json")
SOUND_SETTINGS_FILE = os.path.join(BASE_DIR, "audio_settings.json")

#---Fundos do menu e combate---
MENU_BACKGROUND = os.path.join(BASE_DIR, "assets", "sprites", "backgrounds", "menu_background.png")
COMBAT_BACKGROUND = os.path.join(BASE_DIR, "assets", "sprites", "backgrounds", "combat_background.png")