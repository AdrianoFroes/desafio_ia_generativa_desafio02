"""Testes da revisão humana vinculada à auditoria RF11."""

import hashlib
import tempfile
import unittest
from pathlib import Path

from src.audit import (
    consultar_revisao_humana,
    listar_execucoes,
    registrar_execucao,
)
from src.revisao_humana import revisar_documento


class TestesRevisaoDocumentoRF11(unittest.TestCase):

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temporario.name)
        self.log = self.raiz / "auditoria.jsonl"

        self.documento = self.raiz / "resultados" / "minutas" / "teste.txt"
        self.documento.parent.mkdir(parents=True, exist_ok=True)
        self.documento.write_text(
            "Minuta fictícia para revisão humana.",
            encoding="utf-8"
        )

        self.execucao = registrar_execucao(
            {
                "requisito": "RF09",
                "origem": "minuta",
                "id_caso": "2026-000142",
                "modalidade_entrada": "texto",
                "arquivo_saida": "resultados/minutas/teste.txt",
                "status": "sucesso",
                "revisao_humana": "pendente"
            },
            caminho=self.log
        )

        self.id_execucao = self.execucao["id_execucao"]

    def tearDown(self):
        self.temporario.cleanup()

    def revisar(self, decisao="aprovado", arquivo=None):
        return revisar_documento(
            id_execucao=self.id_execucao,
            decisao=decisao,
            arquivo_revisado=(
                arquivo
                if arquivo is not None
                else "resultados/minutas/teste.txt"
            ),
            caminho_log=self.log,
            raiz_projeto=self.raiz
        )

    def test_aprovacao_registrada(self):
        evento = self.revisar()

        self.assertEqual(evento["decisao"], "aprovado")
        self.assertEqual(
            evento["id_execucao_referenciada"],
            self.id_execucao
        )
        self.assertEqual(
            consultar_revisao_humana(self.id_execucao, self.log),
            "aprovado"
        )

    def test_rejeicao_registrada(self):
        evento = self.revisar("rejeitado")

        self.assertEqual(evento["decisao"], "rejeitado")
        self.assertEqual(
            consultar_revisao_humana(self.id_execucao, self.log),
            "rejeitado"
        )

    def test_hash_corresponde_ao_documento(self):
        evento = self.revisar()

        esperado = hashlib.sha256(
            self.documento.read_bytes()
        ).hexdigest()

        self.assertEqual(
            evento["sha256_documento"],
            esperado
        )
        self.assertEqual(
            evento["arquivo_revisado"],
            "resultados/minutas/teste.txt"
        )

    def test_bloqueia_decisao_duplicada(self):
        self.revisar()

        with self.assertRaises(ValueError):
            self.revisar("rejeitado")

        self.assertEqual(len(listar_execucoes(self.log)), 2)

    def test_rejeita_documento_inexistente(self):
        with self.assertRaises(ValueError):
            self.revisar(
                arquivo="resultados/minutas/inexistente.txt"
            )

        self.assertEqual(len(listar_execucoes(self.log)), 1)

    def test_rejeita_documento_fora_do_projeto(self):
        with self.assertRaises(ValueError):
            self.revisar(arquivo="../documento_externo.txt")

        self.assertEqual(len(listar_execucoes(self.log)), 1)


if __name__ == "__main__":
    unittest.main()
from src.revisao_humana import verificar_integridade_documento


class TestesVinculoIntegridadeRF11(
    unittest.TestCase
):

    setUp = TestesRevisaoDocumentoRF11.setUp
    tearDown = TestesRevisaoDocumentoRF11.tearDown
    revisar = TestesRevisaoDocumentoRF11.revisar

    def test_rejeita_documento_de_outra_execucao(self):
        outro = self.raiz / "resultados" / "minutas" / "outro.txt"
        outro.write_text("Outro caso fictício.", encoding="utf-8")

        with self.assertRaises(ValueError):
            self.revisar(
                arquivo="resultados/minutas/outro.txt"
            )

        self.assertEqual(len(listar_execucoes(self.log)), 1)

    def test_aceita_versao_revisada_correspondente(self):
        revisado = (
            self.raiz / "resultados" / "minutas"
            / "teste_revisada.txt"
        )
        revisado.write_text(
            "Minuta fictícia revisada.",
            encoding="utf-8"
        )

        evento = self.revisar(
            arquivo="resultados/minutas/teste_revisada.txt"
        )

        self.assertEqual(
            evento["arquivo_revisado"],
            "resultados/minutas/teste_revisada.txt"
        )

    def test_detecta_documento_alterado(self):
        self.revisar()

        self.assertTrue(
            verificar_integridade_documento(
                self.id_execucao,
                caminho_log=self.log,
                raiz_projeto=self.raiz
            )
        )

        self.documento.write_text(
            "Conteúdo alterado depois da revisão.",
            encoding="utf-8"
        )

        self.assertFalse(
            verificar_integridade_documento(
                self.id_execucao,
                caminho_log=self.log,
                raiz_projeto=self.raiz
            )
        )
