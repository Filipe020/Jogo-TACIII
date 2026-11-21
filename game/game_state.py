"""Estados do jogo e dados da Run atual"""

from enum import Enum, auto

class GameState(Enum):
    MENU = auto()
    EDITOR = auto()
    LAN_LOBBY = auto()
    RUN = auto()
    PAUSADO = auto()
    SALA_EVOLUCAO = auto()
    GAME_OVER = auto()

class RunState:
    """Guarda o progresso da Run atual. É resetado a cada nova Run e seuvalor é transferido para a Progression ao final"""

    def __init__(self):
        self.inimigos_derrotados = 0
        self.tempo_de_run = 0.0

    def reiniciar(self):
        self.inimigos_derrotados = 0
        self.tempo_de_run = 0.0
