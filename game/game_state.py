"""Estados do jogo e dados da Run atual"""

from enum import Enum, auto

class GameState(Enum):
    MENU = auto()
    EDITOR = auto()
    LAN_LOBBY = auto()
    RUN = auto()
    PAUSADO = auto()
    HABILIDADES = auto()
    SALA_EVOLUCAO = auto()
    GAME_OVER = auto()

class RunState:
    """Guarda as eliminações e o tempo da run atual, reiniciados a cada partida."""

    def __init__(self):
        self.inimigos_derrotados = 0
        self.mobs_derrotados = 0  # apenas inimigos comuns; chefes não contam para o portal
        self.tempo_de_run = 0.0

    def reiniciar(self):
        self.inimigos_derrotados = 0
        self.mobs_derrotados = 0
        self.tempo_de_run = 0.0
