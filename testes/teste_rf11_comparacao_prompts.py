
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import comparacao_prompts
from src.audit import listar_execucoes


class TestesAuditoriaRF02(unittest.TestCase):

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)

        self.raiz = Path(self.temporario.name)
        self.pasta_resultados = self.raiz / "resultados" / "logs"
        self.pasta_prompts = self.raiz / "prompts"
        self.log = self.pasta_resultados / "auditoria.jsonl"

        self.config = {
            "provedor": "gemini",
            "modelo": "gemini-3.8-flash",
            "max_tokens": 1024,
        }

        (self.raiz / "config.json").write_text(
            json.dumps(self.config),
            encoding="utf-8",
        )

    def resposta_simulada(self, prompt, config, chave):
        return {
            "resposta": "Resposta fictícia para o teste.",
            "tempo_segundos": 0.5,
            "tokens_entrada": 10,
            "tokens_saida": 20,
            "tokens_total": 30,
        }

    def executar(self, falhar=False):
        contador = {"chamadas": 0}

        def consultar(prompt, config, chave):
            contador["chamadas"] += 1

            if falhar:
                raise RuntimeError("Falha simulada")

            return self.resposta_simulada(
                prompt, config, chave
            )

        with (
            patch.object(comparacao_prompts, "RAIZ", self.raiz),
            patch.object(
                comparacao_prompts,
                "PASTA_RESULTADOS",
                self.pasta_resultados,
            ),
            patch.object(
                comparacao_prompts,
                "PASTA_PROMPTS",
                self.pasta_prompts,
            ),
            patch.object(
                comparacao_prompts,
                "consultar_gemini",
                side_effect=consultar,
            ),
            patch.object(
                comparacao_prompts,
                "load_dotenv",
            ),
            patch.object(
                comparacao_prompts.os,
                "getenv",
                return_value="CHAVE_FICTICIA",
            ),
            patch(
                "src.audit.ARQUIVO_LOG",
                self.log,
            ),
        ):
            comparacao_prompts.main()

        return contador["chamadas"]

    def test_sucesso_registra_auditoria(self):
        chamadas = self.executar()

        self.assertEqual(chamadas, 4)

        registros = listar_execucoes(self.log)

        self.assertEqual(len(registros), 1)

        registro = registros[0]

        self.assertEqual(registro["requisito"], "RF02")
        self.assertEqual(registro["status"], "sucesso")
        self.assertEqual(registro["tokens_entrada"], 40)
        self.assertEqual(registro["tokens_saida"], 80)
        self.assertEqual(registro["tokens_total"], 120)
        self.assertEqual(registro["tempo_segundos"], 2.0)

        self.assertNotIn(
            "CHAVE_FICTICIA",
            json.dumps(registro),
        )

    def test_falha_registra_erro(self):
        chamadas = self.executar(falhar=True)

        self.assertEqual(chamadas, 1)

        registros = listar_execucoes(self.log)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["requisito"], "RF02")
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"],
            "ERRO_LLM",
        )


if __name__ == "__main__":
    unittest.main()
