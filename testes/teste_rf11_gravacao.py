import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import minuta
from src.audit import listar_execucoes


class TestesFalhaGravacaoRF11(unittest.TestCase):

    def test_falha_metadados_nao_deixa_sucesso_inconsistente(self):
        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta)

            origem = base / "extracao.json"
            prompt = base / "prompt.txt"
            destino = base / "minuta.txt"
            metadados = base / "informacoes.json"
            log = base / "auditoria.jsonl"

            origem.write_text(
                json.dumps({
                    "protocolo": "2026-000142",
                    "assunto": "Matrícula"
                }),
                encoding="utf-8"
            )
            prompt.write_text(
                "Elabore uma minuta fictícia.",
                encoding="utf-8"
            )

            resposta = {
                "provedor": "gemini",
                "modelo": "gemini-3.8-flash",
                "resposta": "Minuta fictícia.",
                "tempo_segundos": 0.5,
                "tokens_entrada": 20,
                "tokens_saida": 30,
                "tokens_total": 50
            }

            config = {
                "provedor": "gemini",
                "modelo": "gemini-3.8-flash",
                "max_tokens": 1024,
                "revisao_humana_obrigatoria": True,
                "envio_automatico": False
            }

            from src.audit import registrar_execucao as original

            def registrar_no_teste(dados, id_execucao=None):
                return original(dados, caminho=log, id_execucao=id_execucao)

            abertura_original = Path.open

            def simular_falha(self, *args, **kwargs):
                modo = args[0] if args else kwargs.get("mode", "r")

                if self == metadados and modo == "xb":
                    raise OSError("Falha simulada nos metadados.")

                return abertura_original(self, *args, **kwargs)

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
                    side_effect=registrar_no_teste
                ),
                patch.object(
                    Path,
                    "open",
                    simular_falha
                )
            ):
                try:
                    minuta.main()
                except OSError:
                    pass

            registros = listar_execucoes(log)

            sucessos = [
                registro for registro in registros
                if registro.get("status") == "sucesso"
            ]

            self.assertFalse(
                destino.exists(),
                "A minuta não deveria permanecer após a falha."
            )

            self.assertFalse(
                metadados.exists(),
                "Os metadados não deveriam permanecer após a falha."
            )

            self.assertEqual(
                sucessos,
                [],
                "A auditoria não deve registrar sucesso após a falha."
            )

            erros_gravacao = [
                registro for registro in registros
                if registro.get("status") == "erro"
                and registro.get("codigo_erro") == "ERRO_GRAVACAO"
            ]

            self.assertEqual(
                len(erros_gravacao),
                1,
                "Deve existir um registro de ERRO_GRAVACAO."
            )


if __name__ == "__main__":
    unittest.main()
