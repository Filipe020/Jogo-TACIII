"""Pontos por inimigo derrotado e habilidades para a partida atual.

Os níveis e pontos podem ser retomados por 'Continuar', mas 'Novo Jogo'
zera a progressão. Testes do editor e partidas LAN usam progresso temporário.
"""

import json
import os

from config import settings

UPGRADE_DEFS = {
    "vida_maxima": {
        "nome": "Vida máxima",
        "descricao": "+20 de vida máxima",
        "custo_base": 5,
        "custo_incremento": 3,
        "max_nivel": 10,
    },
    "dano_espada": {
        "nome": "Dano da espada",
        "descricao": "+8% de dano com a espada",
        "custo_base": 10,
        "custo_incremento": 4,
        "max_nivel": 10,
    },
    "dano_shuriken": {
        "nome": "Dano do shuriken",
        "descricao": "+8% de dano com o shuriken",
        "custo_base": 10,
        "custo_incremento": 4,
        "max_nivel": 10,
    },
    "velocidade": {
        "nome": "Velocidade",
        "descricao": "+5% de velocidade de movimento",
        "custo_base": 15,
        "custo_incremento": 5,
        "max_nivel": 8,
    },
    "qtd_shurikens": {
        "nome": "Quantidade de shurikens",
        "descricao": "+1 shuriken inicial e no máximo",
        "custo_base": 20,
        "custo_incremento": 8,
        "max_nivel": 6,
    },
    "velocidade_ataque": {
        "nome": "Velocidade de ataque",
        "descricao": "-6% no tempo entre ataques",
        "custo_base": 15,
        "custo_incremento": 6,
        "max_nivel": 8,
    },
}


class Progression:
    """Gerencia pontos, compras e eventual persistência de progresso."""

    def __init__(self, carregar=True, persistir=True):
        self.persistir = persistir
        self.pontos_disponiveis = 0
        self.total_inimigos_derrotados = 0
        self.melhor_run = 0
        self.niveis = {chave: 0 for chave in UPGRADE_DEFS}
        if carregar:
            self.carregar()

    def reiniciar_novo_jogo(self):
        """'Novo Jogo' sempre começa do zero, independentemente do save antigo."""
        self.pontos_disponiveis = 0
        self.total_inimigos_derrotados = 0
        self.melhor_run = 0
        self.niveis = {chave: 0 for chave in UPGRADE_DEFS}
        self.salvar()

    # ---Run atual---
    def registrar_kill_run(self, run_state):
        """Cada inimigo rende um ponto imediatamente utilizável durante a run."""
        run_state.inimigos_derrotados += 1
        self.pontos_disponiveis += 1
        self.salvar()

    def encerrar_run(self, run_state):
        """Registra estatísticas, sem creditar novamente os pontos já recebidos."""
        self.total_inimigos_derrotados += run_state.inimigos_derrotados
        self.melhor_run = max(self.melhor_run, run_state.inimigos_derrotados)
        self.salvar()

    # ---Melhorias---
    def custo_proximo_nivel(self, chave):
        info = UPGRADE_DEFS[chave]
        nivel = self.niveis[chave]
        return info["custo_base"] + info["custo_incremento"] * nivel

    def pode_comprar(self, chave):
        info = UPGRADE_DEFS[chave]
        if self.niveis[chave] >= info["max_nivel"]:
            return False
        return self.pontos_disponiveis >= self.custo_proximo_nivel(chave)

    def comprar(self, chave):
        if not self.pode_comprar(chave):
            return False
        custo = self.custo_proximo_nivel(chave)
        self.pontos_disponiveis -= custo
        self.niveis[chave] += 1
        self.salvar()
        return True

    def receber_estado_remoto(self, dados):
        """Atualização da LAN: apenas o servidor pode gastar pontos."""
        if not isinstance(dados, dict):
            return
        pontos = dados.get("points")
        niveis = dados.get("levels")
        if isinstance(pontos, int) and pontos >= 0:
            self.pontos_disponiveis = pontos
        if isinstance(niveis, dict):
            for chave, info in UPGRADE_DEFS.items():
                valor = niveis.get(chave)
                if type(valor) is int and 0 <= valor <= info["max_nivel"]:
                    self.niveis[chave] = valor

    def estado_rede(self):
        return {"points": self.pontos_disponiveis, "levels": dict(self.niveis)}

    # ---Multiplicadores/bônus aplicados ao Player---
    def bonus_vida_maxima(self):
        return self.niveis["vida_maxima"] * 20

    def multiplicador_dano_espada(self):
        return 1.0 + self.niveis["dano_espada"] * 0.08

    def multiplicador_dano_shuriken(self):
        return 1.0 + self.niveis["dano_shuriken"] * 0.08

    def multiplicador_velocidade(self):
        return 1.0 + self.niveis["velocidade"] * 0.05

    def bonus_shurikens(self):
        return self.niveis["qtd_shurikens"]

    def multiplicador_velocidade_ataque(self):
        return max(0.4, 1.0 - self.niveis["velocidade_ataque"] * 0.06)

    # ---Persistência---
    def salvar(self):
        if not self.persistir:
            return
        dados = {
            "pontos_disponiveis": self.pontos_disponiveis,
            "total_inimigos_derrotados": self.total_inimigos_derrotados,
            "melhor_run": self.melhor_run,
            "niveis": self.niveis,
        }
        try:
            with open(settings.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def carregar(self):
        if not os.path.exists(settings.SAVE_FILE):
            return
        try:
            with open(settings.SAVE_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self.pontos_disponiveis = max(0, int(dados.get("pontos_disponiveis", 0)))
            self.total_inimigos_derrotados = max(0, int(dados.get("total_inimigos_derrotados", 0)))
            self.melhor_run = max(0, int(dados.get("melhor_run", 0)))
            niveis = dados.get("niveis", {})
            for chave, info in UPGRADE_DEFS.items():
                self.niveis[chave] = max(0, min(info["max_nivel"], int(niveis.get(chave, 0))))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            pass
