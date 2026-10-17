"""Testes de proteção contra sobrescrita no RF11."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import minuta
from src.audit import listar_execucoes


class TestesProtecaoSobrescritaRF11(unittest.TestCase):

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)

        self.raiz = Path(self.temporario.name)

        self.origem = self.raiz / "extracao.json"
        self.prompt = self.raiz / "prompt.txt"
        self.destino = self.raiz / "minuta.txt"
        self.metadados = self.raiz / "informacoes.json"
        self.log = self.raiz / "auditoria.jsonl"

        self.origem.write_text(
            json.dumps({
                "protocolo": "2026-000142",
                "assunto": "Matrícula"
            }),
            encoding="utf-8"
        )

        self.prompt.write_text(
            "Elabore uma minuta institucional fictícia.",
            encoding="utf-8"
        )

        self.config = {
            "provedor": "gemini",
            "modelo": "gemini-3.8-flash",
            "max_tokens": 1024,
            "revisao_humana_obrigatoria": True,
            "envio_automatico": False
        }

    def executar(self, codigo_esperado="SAIDA_JA_EXISTENTE"):
        from src.audit import registrar_execucao as registrar_original

        def registrar_no_teste(dados):
            return registrar_original(
                dados,
                caminho=self.log
            )

        with (
            patch.object(minuta, "ORIGEM", self.origem),
            patch.object(minuta, "PROMPT", self.prompt),
            patch.object(minuta, "DESTINO", self.destino),
            patch.object(minuta, "METADADOS", self.metadados),
            patch.object(
                minuta,
                "carregar_configuracao",
                return_value=self.config
            ),
            patch.object(
                minuta,
                "registrar_execucao",
                side_effect=registrar_no_teste
            ),
            patch.object(minuta, "gerar_minuta") as gerar
        ):
            minuta.main()

            gerar.assert_not_called()

        registros = listar_execucoes(self.log)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"],
            codigo_esperado
        )

    def test_preserva_minuta_existente(self):
        conteudo_original = "Minuta anteriormente aprovada."
        self.destino.write_text(
            conteudo_original,
            encoding="utf-8"
        )

        self.executar()

        self.assertEqual(
            self.destino.read_text(encoding="utf-8"),
            conteudo_original
        )
        self.assertFalse(self.metadados.exists())

    def test_preserva_metadados_existentes(self):
        conteudo_original = '{"aprovado": true}'
        self.metadados.write_text(
            conteudo_original,
            encoding="utf-8"
        )

        self.executar()

        self.assertEqual(
            self.metadados.read_text(encoding="utf-8"),
            conteudo_original
        )
        self.assertFalse(self.destino.exists())


    def test_bloqueia_protocolo_ausente(self):
        self.origem.write_text(
            json.dumps({"assunto": "Matrícula"}),
            encoding="utf-8"
        )

        self.executar(codigo_esperado="ERRO_DADOS")

        self.assertFalse(self.destino.exists())
        self.assertFalse(self.metadados.exists())

    def test_bloqueia_protocolo_vazio(self):
        self.origem.write_text(
            json.dumps({
                "protocolo": "   ",
                "assunto": "Matrícula"
            }),
            encoding="utf-8"
        )

        self.executar(codigo_esperado="ERRO_DADOS")

        self.assertFalse(self.destino.exists())
        self.assertFalse(self.metadados.exists())


if __name__ == "__main__":
    unittest.main()
