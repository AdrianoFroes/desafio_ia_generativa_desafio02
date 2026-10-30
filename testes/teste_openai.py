import os
import unittest
from unittest.mock import patch

from src.llm_client import (
    ErroLLM,
    LLMAdaptadorOpenAI,
    consultar_llm,
    criar_llm,
)
from src.nlp import extrair_entidades
from src.sentiment import classificar_sentimento


MENSAGENS = [
    {"role": "system", "content": "Responda de forma objetiva."},
    {"role": "user", "content": "O que é um protocolo?"}
]

CONFIG_OPENAI = {
    "provedor": "openai",
    "modelo": "gpt-4o-mini",
    "temperatura": 0.3,
    "max_tokens": 1024
}

RESPOSTA_VALIDA = {
    "choices": [
        {"message": {"role": "assistant", "content": "É um número de registro."}}
    ],
    "usage": {
        "prompt_tokens": 20,
        "completion_tokens": 10,
        "total_tokens": 30
    }
}


class TestesOpenAI(unittest.TestCase):

    def setUp(self):
        patcher = patch(
            "src.llm_client.carregar_configuracao",
            return_value=CONFIG_OPENAI
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_chave_ausente(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with self.assertRaisesRegex(
                ErroLLM, "OPENAI_API_KEY não encontrada"
            ):
                consultar_llm(MENSAGENS)

    @patch("src.llm_client.requests.post")
    def test_autenticacao_invalida(self, mock_post):
        mock_post.return_value.status_code = 401

        with patch.dict(os.environ, {"OPENAI_API_KEY": "chave_ficticia"}):
            with self.assertRaisesRegex(ErroLLM, "Autenticação inválida"):
                consultar_llm(MENSAGENS)

    @patch("src.llm_client.requests.post")
    def test_resposta_vazia(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"choices": []}

        with patch.dict(os.environ, {"OPENAI_API_KEY": "chave_ficticia"}):
            with self.assertRaisesRegex(ErroLLM, "não retornou"):
                consultar_llm(MENSAGENS)

    @patch("src.llm_client.requests.post")
    def test_resposta_valida(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = RESPOSTA_VALIDA

        with patch.dict(os.environ, {"OPENAI_API_KEY": "chave_ficticia"}):
            resultado = consultar_llm(MENSAGENS)

        self.assertEqual(resultado["provedor"], "openai")
        self.assertEqual(resultado["resposta"], "É um número de registro.")
        self.assertEqual(resultado["tokens_entrada"], 20)
        self.assertEqual(resultado["tokens_saida"], 10)
        self.assertEqual(resultado["tokens_total"], 30)

        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.openai.com/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer chave_ficticia")
        self.assertEqual(kwargs["json"]["model"], "gpt-4o-mini")
        self.assertEqual(kwargs["json"]["messages"], MENSAGENS)

    @patch("src.llm_client.requests.post")
    def test_adaptador_completar(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = RESPOSTA_VALIDA

        with patch.dict(os.environ, {"OPENAI_API_KEY": "chave_ficticia"}):
            llm = criar_llm("openai")
            self.assertIsInstance(llm, LLMAdaptadorOpenAI)
            self.assertEqual(llm.completar("Resuma"), "É um número de registro.")

    def test_adaptador_sem_chave_falha(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with self.assertRaises(ValueError):
                criar_llm("openai")


class TestesJsonComCerca(unittest.TestCase):
    """LLMs reais costumam devolver o JSON dentro de ```json ... ```."""

    class LLMComCerca:
        def __init__(self, conteudo):
            self.conteudo = conteudo

        def completar(self, prompt, **kwargs):
            return f"```json\n{self.conteudo}\n```"

    def test_entidades_com_cerca(self):
        llm = self.LLMComCerca(
            '{"entidades": [{"tipo": "orgao", "valor": "ETEC", "origem": "literal"}], "ausentes": []}'
        )
        entidades, ausentes = extrair_entidades("Quero me inscrever na ETEC.", llm)
        self.assertEqual([(e.tipo, e.valor) for e in entidades], [("orgao", "ETEC")])
        self.assertEqual(ausentes, [])

    def test_sentimento_com_cerca(self):
        llm = self.LLMComCerca('{"polaridade": "positiva", "justificativa": "Elogio"}')
        self.assertEqual(
            classificar_sentimento("Otimo atendimento!", llm),
            ("positiva", "Elogio")
        )


if __name__ == "__main__":
    unittest.main()
