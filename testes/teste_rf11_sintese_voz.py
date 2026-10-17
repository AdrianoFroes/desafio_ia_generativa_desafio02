
import json
import sys
import tempfile
import unittest
import base64
import wave
from unittest.mock import Mock
from pathlib import Path
from unittest.mock import patch

from src import sintese_voz
from src.audit import listar_execucoes


class TestesAuditoriaVozRF11(unittest.TestCase):

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)

        self.raiz = Path(self.temporario.name)
        self.log = self.raiz / "auditoria.jsonl"

        patch_raiz = patch.object(sintese_voz, "RAIZ", self.raiz)
        patch_log = patch("src.audit.ARQUIVO_LOG", self.log)

        patch_raiz.start()
        patch_log.start()

        self.addCleanup(patch_raiz.stop)
        self.addCleanup(patch_log.stop)

        self.minuta = self.raiz / "resultados" / "minutas" / "minuta.txt"
        self.minuta.parent.mkdir(parents=True, exist_ok=True)
        self.minuta.write_text(
            "Minuta fictícia aprovada.",
            encoding="utf-8",
        )

        self.audio = (
            self.raiz / "resultados" / "audios"
            / "rf07_minuta_falada.wav"
        )
        self.info = (
            self.raiz / "resultados" / "audios"
            / "rf07_informacoes.json"
        )

    def executar(self):
        with patch.object(
            sys,
            "argv",
            [
                "sintese_voz.py",
                str(self.minuta),
                "--aprovado",
            ],
        ):
            sintese_voz.main()

    def resultado_simulado(self, id_execucao):
        self.audio.parent.mkdir(parents=True, exist_ok=True)
        self.audio.write_bytes(b"audio simulado")

        dados = {
            "modelo": sintese_voz.MODELO,
            "voz": sintese_voz.VOZ,
            "arquivo_audio": str(self.audio),
            "tempo_segundos": 0.5,
            "tokens_total": 30,
            "id_execucao": id_execucao,
        }

        self.info.write_text(
            json.dumps(dados),
            encoding="utf-8",
        )

        return dados

    def test_sucesso_registra_auditoria(self):
        with patch.object(
            sintese_voz,
            "sintetizar_minuta",
            side_effect=lambda *args, **kwargs:
                self.resultado_simulado(kwargs["id_execucao"]),
        ):
            self.executar()

        registros = listar_execucoes(self.log)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["requisito"], "RF07")
        self.assertEqual(registros[0]["status"], "sucesso")
        self.assertEqual(registros[0]["tokens_total"], 30)

        informacoes = json.loads(
            self.info.read_text(encoding="utf-8")
        )

        self.assertEqual(
            informacoes["id_execucao"],
            registros[0]["id_execucao"],
        )

    def test_arquivos_existentes_sao_preservados(self):
        self.audio.parent.mkdir(parents=True, exist_ok=True)
        self.audio.write_bytes(b"audio historico")
        self.info.write_text(
            '{"historico": true}',
            encoding="utf-8",
        )

        with patch.object(
            sintese_voz,
            "sintetizar_minuta",
        ) as consulta:
            with self.assertRaises(SystemExit):
                self.executar()

        consulta.assert_not_called()

        self.assertEqual(
            self.audio.read_bytes(),
            b"audio historico",
        )

        self.assertEqual(
            json.loads(self.info.read_text(encoding="utf-8")),
            {"historico": True},
        )

        registros = listar_execucoes(self.log)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"],
            "ARQUIVO_EXISTENTE",
        )

    def test_falha_sintese_registra_erro(self):
        with patch.object(
            sintese_voz,
            "sintetizar_minuta",
            side_effect=RuntimeError("Falha simulada."),
        ):
            with self.assertRaises(SystemExit):
                self.executar()

        self.assertFalse(self.audio.exists())
        self.assertFalse(self.info.exists())

        registros = listar_execucoes(self.log)

        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"],
            "ERRO_SINTESE",
        )

    def test_falha_auditoria_remove_arquivos(self):
        with (
            patch.object(
                sintese_voz,
                "sintetizar_minuta",
                side_effect=lambda *args, **kwargs:
                    self.resultado_simulado(kwargs["id_execucao"]),
            ),
            patch.object(
                sintese_voz,
                "registrar_execucao",
                side_effect=OSError("Falha simulada na auditoria."),
            ),
        ):
            with self.assertRaises(OSError):
                self.executar()

        self.assertFalse(self.audio.exists())
        self.assertFalse(self.info.exists())


    def test_gravacao_real_wav_json_com_http_simulado(self):
        # PCM mono, 16 bits: quatro amostras fictícias.
        audio_pcm = b"\x00\x00\x01\x00\xff\xff\x02\x00"

        resposta = Mock()
        resposta.status_code = 200
        resposta.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "inlineData": {
                                    "mimeType": "audio/L16;rate=24000",
                                    "data": base64.b64encode(
                                        audio_pcm
                                    ).decode("ascii"),
                                }
                            }
                        ]
                    }
                }
            ],
            "usageMetadata": {
                "totalTokenCount": 45
            },
        }

        with (
            patch.object(
                sintese_voz,
                "load_dotenv",
            ),
            patch.object(
                sintese_voz.os,
                "getenv",
                return_value="CHAVE_FICTICIA",
            ),
            patch.object(
                sintese_voz.requests,
                "post",
                return_value=resposta,
            ) as consulta,
        ):
            self.executar()

        consulta.assert_called_once()

        self.assertTrue(self.audio.is_file())
        self.assertTrue(self.info.is_file())

        with wave.open(str(self.audio), "rb") as arquivo:
            self.assertEqual(arquivo.getnchannels(), 1)
            self.assertEqual(arquivo.getsampwidth(), 2)
            self.assertEqual(arquivo.getframerate(), 24000)
            self.assertEqual(arquivo.readframes(4), audio_pcm)

        informacoes = json.loads(
            self.info.read_text(encoding="utf-8")
        )

        registros = listar_execucoes(self.log)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["requisito"], "RF07")
        self.assertEqual(registros[0]["status"], "sucesso")

        self.assertEqual(informacoes["tokens_total"], 45)
        self.assertTrue(
            informacoes["revisao_audio_pendente"]
        )
        self.assertEqual(
            informacoes["id_execucao"],
            registros[0]["id_execucao"],
        )

        self.assertNotIn(
            "CHAVE_FICTICIA",
            self.log.read_text(encoding="utf-8"),
        )



if __name__ == "__main__":
    unittest.main()
