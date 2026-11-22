"""Testes do novo fluxo de pontos e reinício (não precisam abrir janela)."""
import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from config import settings
from systems.progression import Progression, UPGRADE_DEFS


class ProgressionDuringRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.save = os.path.join(self.tmp.name, "savegame.json")
        patcher = patch.object(settings, "SAVE_FILE", self.save)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_kills_generate_points_immediately_but_not_twice_after_death(self):
        progress = Progression()
        run = SimpleNamespace(inimigos_derrotados=0)
        for _ in range(5):
            progress.registrar_kill_run(run)
        self.assertEqual(progress.pontos_disponiveis, 5)
        self.assertEqual(run.inimigos_derrotados, 5)
        self.assertTrue(progress.comprar("vida_maxima"))
        self.assertEqual(progress.niveis["vida_maxima"], 1)
        self.assertEqual(progress.pontos_disponiveis, 0)
        progress.encerrar_run(run)
        self.assertEqual(progress.pontos_disponiveis, 0)
        self.assertEqual(progress.total_inimigos_derrotados, 5)

    def test_novo_jogo_zera_habilidades_pontos_estatisticas_e_salva(self):
        progress = Progression()
        progress.pontos_disponiveis = 50
        progress.niveis["dano_espada"] = 3
        progress.niveis["velocidade"] = 2
        progress.total_inimigos_derrotados = 80
        progress.melhor_run = 30
        progress.salvar()

        progress.reiniciar_novo_jogo()
        self.assertEqual(progress.pontos_disponiveis, 0)
        self.assertEqual(progress.total_inimigos_derrotados, 0)
        self.assertEqual(progress.melhor_run, 0)
        self.assertTrue(all(v == 0 for v in progress.niveis.values()))
        self.assertTrue(all(v == 0 for v in Progression().niveis.values()))
        with open(self.save, encoding="utf-8") as file:
            self.assertEqual(json.load(file)["pontos_disponiveis"], 0)

    def test_continuar_recarrega_habilidades_do_save(self):
        progress = Progression()
        progress.pontos_disponiveis = 15
        self.assertTrue(progress.comprar("dano_espada"))
        saved = Progression()
        self.assertEqual(saved.niveis["dano_espada"], 1)
        self.assertEqual(saved.pontos_disponiveis, 5)

    def test_testes_e_lan_nao_gravam_progressao_local(self):
        progress = Progression(carregar=False, persistir=False)
        run = SimpleNamespace(inimigos_derrotados=0)
        for _ in range(20):
            progress.registrar_kill_run(run)
        self.assertTrue(progress.comprar("vida_maxima"))
        self.assertFalse(os.path.exists(self.save))

    def test_estado_rede_respeita_limite_e_nao_altera_save(self):
        progress = Progression(carregar=False, persistir=False)
        progress.receber_estado_remoto({"points": 9,
                "levels": {"vida_maxima": 2, "velocidade": 999,
                           "dano_espada": -1, "dano_shuriken": "alto"}})
        self.assertEqual(progress.pontos_disponiveis, 9)
        self.assertEqual(progress.niveis["vida_maxima"], 2)
        self.assertEqual(progress.niveis["velocidade"], 0)
        self.assertEqual(progress.niveis["dano_espada"], 0)
        self.assertFalse(os.path.exists(self.save))


if __name__ == "__main__":
    unittest.main()
