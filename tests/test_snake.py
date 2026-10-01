import tempfile
import unittest
from pathlib import Path

from snake_game import Partida, COLUNAS, LINHAS, carregar_recordes, salvar_recordes


class RegrasTest(unittest.TestCase):
    def test_comer_cresce_e_pontua(self):
        p = Partida()
        p.comida = (8, 10)
        p.avancar()
        self.assertEqual((len(p.cobra), p.pontos), (4, 10))
        self.assertNotIn(p.comida, p.cobra)

    def test_reversao_e_dupla_curva_bloqueadas(self):
        p = Partida()
        p.virar((-1, 0))
        self.assertEqual(p.proxima, (1, 0))
        p.virar((0, -1))
        p.virar((-1, 0))
        p.avancar()
        self.assertEqual(p.cobra[0], (7, 9))

    def test_parede_e_borda_livre(self):
        for livre in (False, True):
            p = Partida(livre=livre)
            p.cobra = [(COLUNAS - 1, 0)]
            p.comida = (10, 10)
            p.avancar()
            self.assertEqual(p.terminou, not livre)
            if livre:
                self.assertEqual(p.cobra[0], (0, 0))

    def test_colisao_corpo(self):
        p = Partida()
        p.cobra = [(2, 2), (2, 3), (3, 3), (3, 2), (4, 2)]
        p.avancar()
        self.assertTrue(p.terminou)

    def test_pode_entrar_na_cauda_que_sai(self):
        p = Partida()
        p.cobra = [(2, 2), (2, 3), (3, 3), (3, 2)]
        p.comida = (10, 10)
        p.avancar()
        self.assertFalse(p.terminou)
        self.assertEqual(p.cobra[0], (3, 2))

    def test_vitoria_tabuleiro_cheio(self):
        p = Partida()
        p.cobra = [(0, 0)] + [(x, y) for y in range(LINHAS) for x in range(COLUNAS) if (x, y) not in ((0, 0), (1, 0))]
        p.comida = (1, 0)
        p.avancar()
        self.assertTrue(p.venceu and p.terminou)
        self.assertIsNone(p.comida)

    def test_nivel_velocidade_e_reinicio(self):
        p = Partida()
        p.pontos = 50
        self.assertEqual((p.nivel, p.velocidade), (2, 10))
        p.pontos = 5000
        self.assertEqual(p.velocidade, 22)
        self.assertEqual(Partida().pontos, 0)

    def test_recordes_e_arquivo_invalido(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "recordes.json"
            self.assertEqual(carregar_recordes(arquivo), {})
            self.assertTrue(salvar_recordes({"Normal:False": 100}, arquivo))
            self.assertEqual(carregar_recordes(arquivo), {"Normal:False": 100})
            arquivo.write_text("invalido")
            self.assertEqual(carregar_recordes(arquivo), {})


if __name__ == "__main__":
    unittest.main()
