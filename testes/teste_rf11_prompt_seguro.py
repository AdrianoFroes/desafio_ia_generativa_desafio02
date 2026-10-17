
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import prompt_seguro


class TestesAuditoriaRF03(unittest.TestCase):

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)

        self.pasta = Path(self.temporario.name)
        self.log = self.pasta / "auditoria.jsonl"

        self.config = {
            "provedor": "gemini",
            "modelo": "gemini-3.8-flash",
            "max_tokens": 1024,
        }
        (self.pasta / "config.json").write_text(
            json.dumps(self.config, ensure_ascii=False),
            encoding="utf-8",
        )

        self.resultado = {
            "protocolo": "2026/001234",
            "situacao": "Encaminhado para análise do setor responsável",
            "prazo": "não localizado",
            "minuta": "Sua solicitação está em análise.",
            "revisao_humana": True,
        }

    def executar(self, falhar=False):
        def consultar(*args, **kwargs):
            if falhar:
                raise RuntimeError("Falha simulada")
            return self.resultado.copy()

        with (
            patch.object(prompt_seguro, "RAIZ", self.pasta),
            patch.object(
                prompt_seguro,
                "consultar_gemini",
                side_effect=consultar,
            ) as consulta,
            patch.object(
                prompt_seguro,
                "load_dotenv",
            ),
            patch.object(
                prompt_seguro.os,
                "getenv",
                return_value="CHAVE_FICTICIA",
            ),
            patch(
                "src.audit.ARQUIVO_LOG",
                self.log,
            ),
        ):
            prompt_seguro.main()

        return consulta

    def ler_eventos(self):
        if not self.log.exists():
            return []

        return [
            json.loads(linha)
            for linha in self.log.read_text(
                encoding="utf-8"
            ).splitlines()
            if linha.strip()
        ]

    def test_registra_dois_sucessos(self):
        consulta = self.executar()

        self.assertEqual(consulta.call_count, 2)

        eventos = self.ler_eventos()
        self.assertEqual(len(eventos), 2)

        identificadores = set()

        for evento in eventos:
            self.assertEqual(evento["requisito"], "RF03")
            self.assertEqual(evento["status"], "sucesso")
            self.assertEqual(
                evento["revisao_humana"],
                "pendente",
            )
            self.assertNotIn(
                "CHAVE_FICTICIA",
                json.dumps(evento),
            )
            identificadores.add(evento["id_execucao"])

        self.assertEqual(len(identificadores), 2)

        for nome in ("normal", "injecao"):
            arquivo = (
                self.pasta
                / "resultados"
                / "logs"
                / f"rf03_{nome}.json"
            )
            self.assertTrue(arquivo.is_file())

            dados = json.loads(
                arquivo.read_text(encoding="utf-8")
            )

            self.assertIn(
                dados["id_execucao"],
                identificadores,
            )

    def test_registra_falhas(self):
        consulta = self.executar(falhar=True)

        self.assertEqual(consulta.call_count, 2)

        eventos = self.ler_eventos()
        self.assertEqual(len(eventos), 2)

        for evento in eventos:
            self.assertEqual(evento["status"], "erro")
            self.assertEqual(
                evento["codigo_erro"],
                "ERRO_LLM",
            )

    def test_nao_sobrescreve_resultados(self):
        pasta = self.pasta / "resultados" / "logs"
        pasta.mkdir(parents=True, exist_ok=True)

        existente = pasta / "rf03_normal.json"
        existente.write_text(
            '{"historico": true}',
            encoding="utf-8",
        )

        self.executar()

        self.assertEqual(
            existente.read_text(encoding="utf-8"),
            '{"historico": true}',
        )

        eventos = self.ler_eventos()

        self.assertEqual(len(eventos), 2)
        self.assertEqual(eventos[0]["status"], "erro")
        self.assertEqual(
            eventos[0]["codigo_erro"],
            "ARQUIVO_EXISTENTE",
        )


if __name__ == "__main__":
    unittest.main()
