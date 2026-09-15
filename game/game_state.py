"""Estados do jogo (GDD seção 31 - Fluxo de Estados) e dados da Run atual
(GDD seção 13 - Contador de Inimigos Derrotados)."""

from enum import Enum, auto


class GameState(Enum):
    MENU = auto()
    RUN = auto()
    PAUSADO = auto()
    SALA_EVOLUCAO = auto()
    GAME_OVER = auto()


class RunState:
    """Guarda o progresso da Run atual. É resetado a cada nova Run e seu
    valor é transferido para a Progression ao final (GDD seção 17)."""

    def __init__(self):
        self.inimigos_derrotados = 0
        self.tempo_de_run = 0.0

    def reiniciar(self):
        self.inimigos_derrotados = 0
        self.tempo_de_run = 0.0
