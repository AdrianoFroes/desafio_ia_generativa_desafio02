import json
import tempfile
import unittest
from pathlib import Path

from src.audit import (
    listar_execucoes,
    registrar_execucao,
    validar_registro,
)


class TestesRF11(unittest.TestCase):

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.arquivo = Path(self.pasta.name) / "auditoria.jsonl"

        self.dados = {
            "requisito": "RF09",
            "origem": "minuta",
            "provedor": "gemini",
            "modelo": "gemini-3.8-flash",
            "versao_prompt": "rf09_v1",
            "status": "sucesso",
            "tempo_segundos": 2.5,
            "tokens_entrada": 100,
            "tokens_saida": 200,
            "tokens_total": 300,
            "revisao_humana": "aprovado",
            "parametros": {
                "max_tokens": 1024,
                "thinking_level": "low"
            }
        }

    def tearDown(self):
        self.pasta.cleanup()

    def test_registro_valido(self):
        registro = registrar_execucao(
            self.dados, caminho=self.arquivo
        )

        self.assertEqual(registro["status"], "sucesso")
        self.assertIn("id_execucao", registro)
        self.assertIn("data_hora", registro)
        self.assertTrue(self.arquivo.exists())

    def test_registros_nao_sao_sobrescritos(self):
        registrar_execucao(self.dados, caminho=self.arquivo)
        registrar_execucao(self.dados, caminho=self.arquivo)

        registros = listar_execucoes(self.arquivo)

        self.assertEqual(len(registros), 2)
        self.assertNotEqual(
            registros[0]["id_execucao"],
            registros[1]["id_execucao"]
        )

    def test_bloqueia_chave_api(self):
        dados = dict(self.dados)
        dados["api_key"] = "segredo-ficticio"

        with self.assertRaises(ValueError):
            registrar_execucao(dados, caminho=self.arquivo)

        self.assertFalse(self.arquivo.exists())

    def test_bloqueia_texto_da_solicitacao(self):
        dados = dict(self.dados)
        dados["mensagem_usuario"] = "Dados pessoais fictícios"

        with self.assertRaises(ValueError):
            registrar_execucao(dados, caminho=self.arquivo)

    def test_status_invalido(self):
        dados = dict(self.dados)
        dados["status"] = "publicado"

        with self.assertRaises(ValueError):
            validar_registro(dados)

    def test_revisao_invalida(self):
        dados = dict(self.dados)
        dados["revisao_humana"] = "automaticamente_aprovado"

        with self.assertRaises(ValueError):
            validar_registro(dados)

    def test_registro_de_erro(self):
        dados = {
            "requisito": "RF04",
            "origem": "llm",
            "provedor": "gemini",
            "modelo": "gemini-3.8-flash",
            "status": "erro",
            "codigo_erro": "HTTP_429",
            "revisao_humana": "nao_aplicavel"
        }

        registro = registrar_execucao(
            dados, caminho=self.arquivo
        )

        self.assertEqual(registro["codigo_erro"], "HTTP_429")

    def test_lista_vazia(self):
        self.assertEqual(
            listar_execucoes(self.arquivo), []
        )

    def test_arquivo_corrompido(self):
        self.arquivo.write_text(
            "nao e json\n", encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            listar_execucoes(self.arquivo)

    def test_formato_jsonl(self):
        registrar_execucao(self.dados, caminho=self.arquivo)

        linha = self.arquivo.read_text(
            encoding="utf-8"
        ).strip()

        registro = json.loads(linha)

        self.assertEqual(registro["requisito"], "RF09")


class TestesIntegracaoRF11(unittest.TestCase):

    def setUp(self):
        from unittest.mock import patch
        from src import minuta

        self.minuta = minuta
        self.pasta = tempfile.TemporaryDirectory()
        self.base = Path(self.pasta.name)

        self.origem = self.base / "extracao.json"
        self.prompt = self.base / "prompt.txt"
        self.destino = self.base / "minuta.txt"
        self.metadados = self.base / "informacoes.json"
        self.log = self.base / "auditoria.jsonl"

        self.origem.write_text(
            json.dumps({
                "protocolo": "2026-000142",
                "assunto": "Matrícula",
                "documentos_pendentes": "não localizado"
            }, ensure_ascii=False),
            encoding="utf-8"
        )

        self.prompt.write_text(
            "Elabore uma resposta institucional.",
            encoding="utf-8"
        )

        self.patches = [
            patch.object(minuta, "ORIGEM", self.origem),
            patch.object(minuta, "PROMPT", self.prompt),
            patch.object(minuta, "DESTINO", self.destino),
            patch.object(minuta, "METADADOS", self.metadados),
            patch(
                "src.audit.ARQUIVO_LOG",
                self.log
            ),
            patch.object(
                minuta,
                "carregar_configuracao",
                return_value={
                    "revisao_humana_obrigatoria": True,
                    "envio_automatico": False,
                    "provedor": "gemini",
                    "modelo": "gemini-3.8-flash",
                    "max_tokens": 1024
                }
            )
        ]

        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()

        self.pasta.cleanup()

    def test_integracao_sucesso(self):
        from unittest.mock import patch

        resposta_ficticia = {
            "provedor": "gemini",
            "modelo": "gemini-3.8-flash",
            "resposta": "Minuta fictícia para testes.",
            "tempo_segundos": 0.5,
            "tokens_entrada": 20,
            "tokens_saida": 30,
            "tokens_total": 50
        }

        with patch.object(
            self.minuta,
            "consultar_llm",
            return_value=resposta_ficticia
        ):
            self.minuta.main()

        registros = listar_execucoes(self.log)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "sucesso")
        self.assertEqual(registros[0]["requisito"], "RF09")
        self.assertEqual(
            registros[0]["revisao_humana"], "pendente"
        )
        self.assertTrue(self.destino.exists())

        # Confirma a rastreabilidade da execução.
        registro = registros[0]

        self.assertEqual(
            registro["id_caso"], "2026-000142"
        )
        self.assertEqual(
            registro["modalidade_entrada"], "texto"
        )
        self.assertEqual(
            registro["arquivo_entrada"],
            "dados/originais/entrada_texto.txt"
        )
        self.assertEqual(
            registro["arquivo_processado"],
            "dados/processados/rf05_extracao.json"
        )
        self.assertEqual(
            registro["arquivo_saida"],
            "resultados/minutas/rf09_minuta.txt"
        )

        # Confirma o vínculo entre metadados e auditoria.
        informacoes = json.loads(
            self.metadados.read_text(encoding="utf-8")
        )

        self.assertEqual(
            informacoes["id_execucao"],
            registro["id_execucao"]
        )
        self.assertEqual(
            informacoes["id_caso"],
            registro["id_caso"]
        )
        self.assertFalse(informacoes["aprovado"])
        self.assertFalse(informacoes["enviado"])

    def test_integracao_erro(self):
        from unittest.mock import patch
        from src.llm_client import ErroLLM

        with patch.object(
            self.minuta,
            "consultar_llm",
            side_effect=ErroLLM("Falha simulada.")
        ):
            self.minuta.main()

        registros = listar_execucoes(self.log)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(
            registros[0]["codigo_erro"], "ERRO_LLM"
        )
        self.assertFalse(self.destino.exists())


class TestesDecisaoHumanaRF11(unittest.TestCase):

    def setUp(self):
        from src.audit import registrar_execucao

        self.pasta = tempfile.TemporaryDirectory()
        self.arquivo = Path(self.pasta.name) / "auditoria.jsonl"

        self.execucao = registrar_execucao({
            "requisito": "RF09",
            "origem": "minuta",
            "provedor": "gemini",
            "modelo": "gemini-3.8-flash",
            "status": "sucesso",
            "revisao_humana": "pendente"
        }, caminho=self.arquivo)

        self.id = self.execucao["id_execucao"]

    def tearDown(self):
        self.pasta.cleanup()

    def test_aprovacao_vinculada(self):
        from src.audit import (
            registrar_decisao_humana,
            consultar_revisao_humana
        )

        evento = registrar_decisao_humana(
            self.id, "aprovado", caminho=self.arquivo
        )

        self.assertEqual(
            evento["id_execucao_referenciada"], self.id
        )
        self.assertEqual(
            consultar_revisao_humana(self.id, self.arquivo),
            "aprovado"
        )

    def test_rejeicao_vinculada(self):
        from src.audit import (
            registrar_decisao_humana,
            consultar_revisao_humana
        )

        registrar_decisao_humana(
            self.id, "rejeitado", caminho=self.arquivo
        )

        self.assertEqual(
            consultar_revisao_humana(self.id, self.arquivo),
            "rejeitado"
        )

    def test_revisao_inicial_pendente(self):
        from src.audit import consultar_revisao_humana

        self.assertEqual(
            consultar_revisao_humana(self.id, self.arquivo),
            "pendente"
        )

    def test_bloqueia_decisao_duplicada(self):
        from src.audit import registrar_decisao_humana

        registrar_decisao_humana(
            self.id, "aprovado", caminho=self.arquivo
        )

        with self.assertRaises(ValueError):
            registrar_decisao_humana(
                self.id, "rejeitado", caminho=self.arquivo
            )

    def test_preserva_registro_original(self):
        from src.audit import registrar_decisao_humana

        registrar_decisao_humana(
            self.id, "aprovado", caminho=self.arquivo
        )

        registros = listar_execucoes(self.arquivo)

        self.assertEqual(len(registros), 2)
        self.assertEqual(
            registros[0]["revisao_humana"], "pendente"
        )
        self.assertEqual(
            registros[1]["tipo_evento"], "decisao_humana"
        )


class TestesFalhasIniciaisRF11(unittest.TestCase):

    def setUp(self):
        from unittest.mock import patch
        from src import minuta

        self.minuta = minuta
        self.pasta = tempfile.TemporaryDirectory()
        self.base = Path(self.pasta.name)

        self.origem = self.base / "extracao.json"
        self.prompt = self.base / "prompt.txt"
        self.log = self.base / "auditoria.jsonl"

        self.origem.write_text(
            '{"assunto": "Teste fictício"}',
            encoding="utf-8"
        )
        self.prompt.write_text(
            "Prompt fictício.",
            encoding="utf-8"
        )

        self.config = {
            "revisao_humana_obrigatoria": True,
            "envio_automatico": False,
            "provedor": "gemini",
            "modelo": "gemini-3.8-flash",
            "max_tokens": 1024
        }

        self.patches = [
            patch.object(minuta, "ORIGEM", self.origem),
            patch.object(minuta, "PROMPT", self.prompt),
            patch("src.audit.ARQUIVO_LOG", self.log),
            patch.object(
                minuta,
                "carregar_configuracao",
                side_effect=lambda: self.config
            ),
            patch.object(
                minuta,
                "consultar_llm",
                side_effect=AssertionError(
                    "O Gemini não deveria ser chamado."
                )
            )
        ]

        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()

        self.pasta.cleanup()

    def verificar_erro(self, codigo):
        self.minuta.main()
        registros = listar_execucoes(self.log)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "erro")
        self.assertEqual(registros[0]["codigo_erro"], codigo)

    def test_revisao_desabilitada(self):
        self.config["revisao_humana_obrigatoria"] = False
        self.verificar_erro("REVISAO_DESABILITADA")

    def test_envio_automatico_ativado(self):
        self.config["envio_automatico"] = True
        self.verificar_erro("ENVIO_AUTOMATICO")

    def test_extracao_ausente(self):
        self.origem.unlink()
        self.verificar_erro("EXTRACAO_AUSENTE")

    def test_prompt_ausente(self):
        self.prompt.unlink()
        self.verificar_erro("PROMPT_AUSENTE")


class TestesRastreabilidadeRF11(unittest.TestCase):

    def test_registra_caso_entrada_e_saida(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "auditoria.jsonl"

            registro = registrar_execucao({
                "requisito": "RF09",
                "origem": "minuta",
                "status": "sucesso",
                "revisao_humana": "pendente",
                "id_caso": "2026-000142",
                "modalidade_entrada": "texto",
                "arquivo_entrada": "dados/originais/entrada_texto.txt",
                "arquivo_processado": "dados/processados/rf05_extracao.json",
                "arquivo_saida": "resultados/minutas/rf09_minuta.txt"
            }, caminho)

            self.assertEqual(
                registro["id_caso"], "2026-000142"
            )
            self.assertEqual(
                registro["modalidade_entrada"], "texto"
            )
            self.assertEqual(
                registro["arquivo_saida"],
                "resultados/minutas/rf09_minuta.txt"
            )

            registros = listar_execucoes(caminho)
            self.assertEqual(registros[0], registro)

    def test_rejeita_modalidade_invalida(self):
        with self.assertRaises(ValueError):
            registrar_execucao({
                "requisito": "RF09",
                "status": "sucesso",
                "modalidade_entrada": "desconhecida"
            })

    def test_rejeita_caminho_fora_do_projeto(self):
        with self.assertRaises(ValueError):
            registrar_execucao({
                "requisito": "RF09",
                "status": "sucesso",
                "arquivo_entrada": "../segredos.txt"
            })

    def test_rejeita_identificador_de_caso_invalido(self):
        with self.assertRaises(ValueError):
            registrar_execucao({
                "requisito": "RF09",
                "status": "sucesso",
                "id_caso": "Protocolo com texto livre!"
            })


if __name__ == "__main__":
    unittest.main()
