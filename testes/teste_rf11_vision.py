
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import vision
from src.audit import listar_execucoes


class TestesAuditoriaVisionRF11(unittest.TestCase):

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)

        self.raiz = Path(self.temporario.name)
        self.log = self.raiz / "auditoria.jsonl"

        patch_raiz = patch.object(vision, "RAIZ", self.raiz)
        patch_log = patch("src.audit.ARQUIVO_LOG", self.log)

        patch_raiz.start()
        patch_log.start()

        self.addCleanup(patch_raiz.stop)
        self.addCleanup(patch_log.stop)

        self.origem = (
            self.raiz / "dados" / "originais" /
            "entrada_pdf-imagem.pdf"
        )
        self.origem.parent.mkdir(parents=True, exist_ok=True)
        self.origem.write_bytes(b"PDF simulado")

        self.pasta = self.raiz / "dados" / "processados"
        self.texto = self.pasta / "rf08_texto_bruto.txt"
        self.info = self.pasta / "rf08_informacoes.json"

    def resposta_simulada(self):
        return {
            "modelo": vision.MODELO,
            "arquivo_original": "entrada_pdf-imagem.pdf",
            "texto_bruto": "Texto fictício extraído do PDF.",
            "tempo_segundos": 0.5,
            "tokens_entrada": 12,
            "tokens_saida": 24,
            "tokens_total": 36,
            "revisao_humana_pendente": True,
        }

    def test_sucesso_registra_execucao(self):
        with patch.object(
            vision,
            "extrair_documento",
            return_value=self.resposta_simulada(),
        ):
            vision.main()

        self.assertTrue(self.texto.exists())
        self.assertTrue(self.info.exists())

        registros = listar_execucoes(self.log)
        self.assertEqual(len(registros), 1)

        registro = registros[0]
        self.assertEqual(registro["requisito"], "RF08")
        self.assertEqual(registro["status"], "sucesso")
        self.assertEqual(registro["modalidade_entrada"], "imagem")
        self.assertEqual(registro["revisao_humana"], "pendente")

        informacoes = json.loads(
            self.info.read_text(encoding="utf-8")
        )

        self.assertEqual(
            informacoes["id_execucao"],
            registro["id_execucao"],
        )

        self.assertNotIn(
            "Texto fictício extraído",
            self.log.read_text(encoding="utf-8"),
        )

    def test_preserva_arquivos_existentes(self):
        self.pasta.mkdir(parents=True, exist_ok=True)

        self.texto.write_text(
            "Texto histórico",
            encoding="utf-8",
        )
        self.info.write_text(
            '{"historico": true}',
            encoding="utf-8",
        )

        with patch.object(vision, "extrair_documento") as consulta:
            with self.assertRaises(SystemExit) as saida:
                vision.main()

        self.assertEqual(saida.exception.code, 1)
        consulta.assert_not_called()

        self.assertEqual(
            self.texto.read_text(encoding="utf-8"),
            "Texto histórico",
        )

        self.assertEqual(
            json.loads(self.info.read_text(encoding="utf-8")),
            {"historico": True},
        )

        registros = listar_execucoes(self.log)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"],
            "ARQUIVO_EXISTENTE",
        )

    def test_falha_extracao_registra_erro(self):
        with patch.object(
            vision,
            "extrair_documento",
            side_effect=RuntimeError("Falha simulada."),
        ):
            with self.assertRaises(SystemExit) as saida:
                vision.main()

        self.assertEqual(saida.exception.code, 1)
        self.assertFalse(self.texto.exists())
        self.assertFalse(self.info.exists())

        registros = listar_execucoes(self.log)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"],
            "ERRO_EXTRACAO",
        )

    def test_falha_auditoria_remove_arquivos(self):
        with (
            patch.object(
                vision,
                "extrair_documento",
                return_value=self.resposta_simulada(),
            ),
            patch.object(
                vision,
                "registrar_execucao",
                side_effect=OSError("Falha simulada no log."),
            ),
        ):
            with self.assertRaises(OSError):
                vision.main()

        self.assertFalse(self.texto.exists())
        self.assertFalse(self.info.exists())


if __name__ == "__main__":
    unittest.main()
