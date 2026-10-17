import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import minuta


class TestesFalhaAuditoriaRF11(unittest.TestCase):

    def test_falha_auditoria_remove_arquivos_publicados(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)

            origem = raiz / "extracao.json"
            prompt = raiz / "prompt.txt"
            destino = raiz / "minuta.txt"
            metadados = raiz / "informacoes.json"

            origem.write_text(
                json.dumps({
                    "protocolo": "2026-000142",
                    "assunto": "Matrícula",
                    "documentos_pendentes": "não localizado"
                }),
                encoding="utf-8"
            )

            prompt.write_text(
                "Produza uma minuta institucional fictícia.",
                encoding="utf-8"
            )

            config = {
                "provedor": "gemini",
                "modelo": "gemini-3.8-flash",
                "max_tokens": 1024,
                "revisao_humana_obrigatoria": True,
                "envio_automatico": False
            }

            resposta = {
                "provedor": "gemini",
                "modelo": "gemini-3.8-flash",
                "tempo_segundos": 0.5,
                "tokens_entrada": 20,
                "tokens_saida": 30,
                "tokens_total": 50
            }

            def falha_auditoria(*args, **kwargs):
                raise OSError("Falha simulada na auditoria.")

            with (
                patch.object(minuta, "ORIGEM", origem),
                patch.object(minuta, "PROMPT", prompt),
                patch.object(minuta, "DESTINO", destino),
                patch.object(minuta, "METADADOS", metadados),
                patch.object(
                    minuta,
                    "carregar_configuracao",
                    return_value=config
                ),
                patch.object(
                    minuta,
                    "gerar_minuta",
                    return_value=("Minuta fictícia.", resposta)
                ),
                patch.object(
                    minuta,
                    "registrar_execucao",
                    side_effect=falha_auditoria
                )
            ):
                with self.assertRaises(OSError):
                    minuta.main()

            self.assertFalse(
                destino.exists(),
                "A minuta deve ser removida se a auditoria falhar."
            )

            self.assertFalse(
                metadados.exists(),
                "Os metadados devem ser removidos se a auditoria falhar."
            )


if __name__ == "__main__":
    unittest.main()
