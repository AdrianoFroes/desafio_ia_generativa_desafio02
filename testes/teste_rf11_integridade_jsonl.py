import tempfile
import unittest
from pathlib import Path

from src.audit import listar_execucoes


class TestesIntegridadeJSONLRF11(unittest.TestCase):

    def test_detecta_registro_parcial(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "auditoria.jsonl"

            caminho.write_text(
                '{"id_execucao": "registro-incompleto"',
                encoding="utf-8"
            )

            with self.assertRaises(ValueError):
                listar_execucoes(caminho)


if __name__ == "__main__":
    unittest.main()
