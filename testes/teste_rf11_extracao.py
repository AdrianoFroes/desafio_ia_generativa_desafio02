
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import extracao
from src.audit import listar_execucoes


class TestesAuditoriaExtracaoRF11(unittest.TestCase):

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)

        self.raiz = Path(self.temporario.name)
        self.log = self.raiz / "auditoria.jsonl"

        for alvo, valor in [
            (patch.object(extracao, "RAIZ", self.raiz), None),
            (patch("src.audit.ARQUIVO_LOG", self.log), None),
            (
                patch.object(
                    extracao,
                    "carregar_configuracao",
                    return_value={
                        "modelo": "gemini-3.8-flash",
                        "max_tokens": 1024,
                    },
                ),
                None,
            ),
        ]:
            alvo.start()
            self.addCleanup(alvo.stop)

        self.origem = (
            self.raiz / "dados" / "originais" / "entrada_texto.txt"
        )
        self.origem.parent.mkdir(parents=True, exist_ok=True)
        self.origem.write_text(
            "Protocolo: 2026-000142\n"
            "Data: 16/10/2026\n"
            "Canal: Portal\n"
            "Meu nome é Pessoa Fictícia, "
            "solicito informações sobre matrícula.",
            encoding="utf-8",
        )

        self.destino = (
            self.raiz / "dados" / "processados" / "rf05_extracao.json"
        )

    def interpretacao_simulada(self):
        return {
            "assunto": "Matrícula",
            "pedido": "Informações sobre matrícula",
            "categoria": "matrícula",
            "confianca": "alta",
        }

    def test_sucesso_registra_auditoria(self):
        with patch.object(
            extracao,
            "interpretar_solicitacao",
            return_value=self.interpretacao_simulada(),
        ) as consulta:
            extracao.main()

        consulta.assert_called_once()

        resultado = json.loads(
            self.destino.read_text(encoding="utf-8")
        )
        registros = listar_execucoes(self.log)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["requisito"], "RF05")
        self.assertEqual(registros[0]["status"], "sucesso")
        self.assertEqual(registros[0]["revisao_humana"], "pendente")
        self.assertEqual(
            resultado["id_execucao"],
            registros[0]["id_execucao"],
        )
        self.assertEqual(
            registros[0]["arquivo_saida"],
            "dados/processados/rf05_extracao.json",
        )
        self.assertNotIn(
            "Pessoa Fictícia",
            self.log.read_text(encoding="utf-8"),
        )

    def test_arquivo_existente_nao_e_sobrescrito(self):
        self.destino.parent.mkdir(parents=True, exist_ok=True)
        self.destino.write_text(
            '{"historico": true}',
            encoding="utf-8",
        )

        with patch.object(
            extracao,
            "interpretar_solicitacao",
        ) as consulta:
            with self.assertRaises(SystemExit):
                extracao.main()

        consulta.assert_not_called()
        self.assertEqual(
            json.loads(self.destino.read_text(encoding="utf-8")),
            {"historico": True},
        )

        registros = listar_execucoes(self.log)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"],
            "ARQUIVO_EXISTENTE",
        )

    def test_falha_modelo_registra_erro(self):
        with patch.object(
            extracao,
            "interpretar_solicitacao",
            side_effect=extracao.ErroLLM("Falha simulada."),
        ):
            with self.assertRaises(SystemExit):
                extracao.main()

        self.assertFalse(self.destino.exists())

        registros = listar_execucoes(self.log)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"],
            "ERRO_LLM",
        )

    def test_falha_auditoria_remove_resultado(self):
        with (
            patch.object(
                extracao,
                "interpretar_solicitacao",
                return_value=self.interpretacao_simulada(),
            ),
            patch.object(
                extracao,
                "registrar_execucao",
                side_effect=OSError("Falha simulada no log."),
            ),
        ):
            with self.assertRaises(OSError):
                extracao.main()

        self.assertFalse(self.destino.exists())


if __name__ == "__main__":
    unittest.main()
