
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import audio
from src.audit import listar_execucoes


class TestesAuditoriaAudioRF11(unittest.TestCase):

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)

        self.raiz = Path(self.temporario.name)
        self.log = self.raiz / "auditoria.jsonl"

        self.patch_raiz = patch.object(audio, "RAIZ", self.raiz)
        self.patch_log = patch("src.audit.ARQUIVO_LOG", self.log)

        self.patch_raiz.start()
        self.patch_log.start()

        self.addCleanup(self.patch_raiz.stop)
        self.addCleanup(self.patch_log.stop)

        self.origem = (
            self.raiz / "dados" / "originais" / "entrada_audio.mp3"
        )
        self.origem.parent.mkdir(parents=True, exist_ok=True)
        self.origem.write_bytes(b"audio simulado")

        self.pasta = self.raiz / "dados" / "processados"
        self.texto = self.pasta / "rf06_transcricao.txt"
        self.info = self.pasta / "rf06_informacoes.json"

    def resposta_simulada(self):
        return {
            "modelo": audio.MODELO,
            "transcricao": "Transcrição fictícia para teste.",
            "tempo_segundos": 0.5,
            "tokens_entrada": 10,
            "tokens_saida": 20,
            "tokens_total": 30,
            "revisao_humana": True,
        }

    def test_sucesso_registra_execucao(self):
        with patch.object(
            audio, "transcrever_audio",
            return_value=self.resposta_simulada()
        ):
            audio.main()

        self.assertTrue(self.texto.exists())
        self.assertTrue(self.info.exists())

        registros = listar_execucoes(self.log)
        self.assertEqual(len(registros), 1)

        registro = registros[0]

        self.assertEqual(registro["requisito"], "RF06")
        self.assertEqual(registro["status"], "sucesso")
        self.assertEqual(registro["modalidade_entrada"], "audio")
        self.assertEqual(registro["revisao_humana"], "pendente")

        informacoes = json.loads(
            self.info.read_text(encoding="utf-8")
        )

        self.assertEqual(
            informacoes["id_execucao"],
            registro["id_execucao"]
        )

        self.assertNotIn(
            "Transcrição fictícia",
            self.log.read_text(encoding="utf-8")
        )

    def test_nao_sobrescreve_arquivos_existentes(self):
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.texto.write_text(
            "Transcrição original", encoding="utf-8"
        )
        self.info.write_text(
            '{"historico": true}', encoding="utf-8"
        )

        with patch.object(audio, "transcrever_audio") as consulta:
            audio.main()

        consulta.assert_not_called()

        self.assertEqual(
            self.texto.read_text(encoding="utf-8"),
            "Transcrição original"
        )

        self.assertEqual(
            json.loads(self.info.read_text(encoding="utf-8")),
            {"historico": True}
        )

        registros = listar_execucoes(self.log)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"], "ARQUIVO_EXISTENTE"
        )

    def test_falha_transcricao_registra_erro(self):
        with patch.object(
            audio, "transcrever_audio",
            side_effect=RuntimeError("Falha simulada.")
        ):
            audio.main()

        self.assertFalse(self.texto.exists())
        self.assertFalse(self.info.exists())

        registros = listar_execucoes(self.log)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"], "ERRO_TRANSCRICAO"
        )

    def test_falha_auditoria_desfaz_arquivos(self):
        with (
            patch.object(
                audio, "transcrever_audio",
                return_value=self.resposta_simulada()
            ),
            patch.object(
                audio, "registrar_execucao",
                side_effect=OSError("Falha simulada no log.")
            ),
        ):
            with self.assertRaises(OSError):
                audio.main()

        self.assertFalse(self.texto.exists())
        self.assertFalse(self.info.exists())


if __name__ == "__main__":
    unittest.main()
