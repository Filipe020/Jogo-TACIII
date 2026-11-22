"""Estados do jogo e dados da Run atual"""

from enum import Enum, auto
from config import settings


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
    """Guarda as eliminações, o tempo e o progresso de fase da run atual, reiniciados a cada partida."""

    def __init__(self, meta_inimigos=None):
        self.meta_inimigos = max(1, int(meta_inimigos if meta_inimigos is not None else settings.INIMIGOS_PARA_CHEFE))
        self.inimigos_derrotados = 0
        self.inimigos_spawnados = 0
        self.tempo_de_run = 0.0
        self.fase_atual = 1       # 1 = Fase Normal, 2 = Fase Final
        self.porta_liberada = False

    def reiniciar(self, meta_inimigos=None):
        if meta_inimigos is not None:
            self.meta_inimigos = max(1, int(meta_inimigos))
        self.inimigos_derrotados = 0
        self.inimigos_spawnados = 0
        self.tempo_de_run = 0.0
        self.fase_atual = 1
        self.porta_liberada = False