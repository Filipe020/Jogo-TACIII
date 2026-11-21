"""Configurações globais do Shadow Rebirth"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#---Janela---

'''Deixar no projeto final em FullScream'''

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TITLE = "Shadow Rebirth"

#---Física---
GRAVITY = 1800.0          #Gravidade
MAX_FALL_SPEED = 1200.0   #Velocidade da queda
MOVE_SPEED = 260.0        #Velocidade do Personagem
JUMP_POWER = 620.0        #Velocidade do Salto

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
}

#---Controles---
# A / D              -> mover
# W ou ESPAÇO        -> pular
# Clique esquerdo    -> espada
# Clique direito     -> shuriken
# ESC                -> pausar / abrir menu
# Enter              -> confirmar seleção

#---Save---
SAVE_FILE = os.path.join(BASE_DIR, "savegame.json")

#---Fundos do menu e combate---
MENU_BACKGROUND = os.path.join(BASE_DIR, "assets", "sprites", "backgrounds", "menu_background.png")
COMBAT_BACKGROUND = os.path.join(BASE_DIR, "assets", "sprites", "backgrounds", "combat_background.png")
