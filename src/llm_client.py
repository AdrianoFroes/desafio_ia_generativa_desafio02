import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


RAIZ = Path(__file__).resolve().parent.parent


class ErroLLM(Exception):
    """Erro durante uma consulta ao modelo de linguagem."""


def carregar_configuracao():
    with (RAIZ / "config.json").open(
        "r", encoding="utf-8-sig"
    ) as arquivo:
        return json.load(arquivo)


CHAVES_PROVEDOR = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY"
}

ERROS_HTTP = {
    400: "Requisição inválida.",
    401: "Autenticação inválida.",
    403: "Acesso não autorizado.",
    404: "Modelo não encontrado ou indisponível.",
    429: "Limite de requisições ou cota atingida.",
    500: "Erro interno do provedor.",
    502: "Erro de comunicação com o provedor.",
    503: "Serviço temporariamente indisponível.",
    504: "Tempo limite do serviço excedido."
}


def consultar_llm(
    mensagens,
    modelo=None,
    max_tokens=None,
    timeout=90,
    thinking_level="low",
    provedor=None
):
    load_dotenv(RAIZ / ".env")

    config = carregar_configuracao()
    provedor = provedor or config.get("provedor")

    if provedor not in CHAVES_PROVEDOR:
        raise ErroLLM(
            f"Provedor não suportado: {provedor}"
        )

    nome_chave = CHAVES_PROVEDOR[provedor]
    chave = os.getenv(nome_chave)

    if not chave:
        raise ErroLLM(
            f"Chave {nome_chave} não encontrada."
        )

    modelo = (
        modelo
        or config.get("modelos", {}).get(provedor)
        or config["modelo"]
    )
    max_tokens = max_tokens or config["max_tokens"]

    if provedor == "openai":
        return _consultar_openai(
            mensagens,
            chave,
            modelo,
            max_tokens,
            config.get("temperatura"),
            timeout
        )

    if not isinstance(mensagens, list) or not mensagens:
        raise ErroLLM("A lista de mensagens está vazia.")

    instrucao_sistema = []
    conteudos = []

    for mensagem in mensagens:
        papel = mensagem.get("role")
        texto = mensagem.get("content")

        if not isinstance(texto, str) or not texto.strip():
            raise ErroLLM("Mensagem sem conteúdo válido.")

        if papel == "system":
            instrucao_sistema.append(texto)

        elif papel in ("user", "assistant"):
            conteudos.append({
                "role": "model" if papel == "assistant" else "user",
                "parts": [{"text": texto}]
            })

        else:
            raise ErroLLM(
                f"Papel de mensagem não suportado: {papel}"
            )

    if not conteudos:
        raise ErroLLM("Nenhuma mensagem de usuário ou assistente.")

    corpo = {
        "contents": conteudos,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "thinkingConfig": {
                "thinkingLevel": thinking_level
            }
        }
    }

    if instrucao_sistema:
        corpo["systemInstruction"] = {
            "parts": [
                {"text": "\n\n".join(instrucao_sistema)}
            ]
        }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{modelo}:generateContent"
    )

    inicio = time.perf_counter()

    try:
        resposta = requests.post(
            url,
            headers={
                "x-goog-api-key": chave,
                "Content-Type": "application/json"
            },
            json=corpo,
            timeout=timeout
        )

    except requests.Timeout as erro:
        raise ErroLLM(
            "Tempo limite excedido na consulta à API."
        ) from erro

    except requests.RequestException as erro:
        raise ErroLLM(
            "Não foi possível conectar ao serviço Gemini."
        ) from erro

    tempo = round(time.perf_counter() - inicio, 2)

    if resposta.status_code != 200:
        _levantar_erro_http(resposta.status_code)

    try:
        dados = resposta.json()
    except ValueError as erro:
        raise ErroLLM(
            "A API retornou dados inválidos."
        ) from erro

    partes = []

    for candidato in dados.get("candidates", []):
        for parte in candidato.get("content", {}).get("parts", []):
            if isinstance(parte.get("text"), str):
                partes.append(parte["text"])

    texto = "\n".join(partes).strip()

    if not texto:
        raise ErroLLM(
            "A API não retornou uma resposta de texto."
        )

    uso = dados.get("usageMetadata", {})

    return {
        "provedor": "gemini",
        "modelo": modelo,
        "resposta": texto,
        "tempo_segundos": tempo,
        "tokens_entrada": uso.get("promptTokenCount"),
        "tokens_saida": uso.get("candidatesTokenCount"),
        "tokens_total": uso.get("totalTokenCount"),
        "custo_estimado_usd": None,
        "observacao_custo": (
            "Não calculado: preços por token não "
            "configurados neste projeto."
        )
    }


def _levantar_erro_http(status_code):
    mensagem = ERROS_HTTP.get(
        status_code,
        "Erro desconhecido na API."
    )

    raise ErroLLM(
        f"{mensagem} HTTP {status_code}."
    )


def _consultar_openai(
    mensagens,
    chave,
    modelo,
    max_tokens,
    temperatura,
    timeout
):
    if not isinstance(mensagens, list) or not mensagens:
        raise ErroLLM("A lista de mensagens está vazia.")

    for mensagem in mensagens:
        papel = mensagem.get("role")
        texto = mensagem.get("content")

        if not isinstance(texto, str) or not texto.strip():
            raise ErroLLM("Mensagem sem conteúdo válido.")

        if papel not in ("system", "user", "assistant"):
            raise ErroLLM(
                f"Papel de mensagem não suportado: {papel}"
            )

    if not any(m["role"] in ("user", "assistant") for m in mensagens):
        raise ErroLLM("Nenhuma mensagem de usuário ou assistente.")

    corpo = {
        "model": modelo,
        "messages": [
            {"role": m["role"], "content": m["content"]}
            for m in mensagens
        ],
        "max_completion_tokens": max_tokens
    }

    if temperatura is not None:
        corpo["temperature"] = temperatura

    inicio = time.perf_counter()

    try:
        resposta = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {chave}",
                "Content-Type": "application/json"
            },
            json=corpo,
            timeout=timeout
        )

    except requests.Timeout as erro:
        raise ErroLLM(
            "Tempo limite excedido na consulta à API."
        ) from erro

    except requests.RequestException as erro:
        raise ErroLLM(
            "Não foi possível conectar ao serviço OpenAI."
        ) from erro

    tempo = round(time.perf_counter() - inicio, 2)

    if resposta.status_code != 200:
        _levantar_erro_http(resposta.status_code)

    try:
        dados = resposta.json()
    except ValueError as erro:
        raise ErroLLM(
            "A API retornou dados inválidos."
        ) from erro

    partes = []

    for escolha in dados.get("choices", []):
        conteudo = escolha.get("message", {}).get("content")
        if isinstance(conteudo, str):
            partes.append(conteudo)

    texto = "\n".join(partes).strip()

    if not texto:
        raise ErroLLM(
            "A API não retornou uma resposta de texto."
        )

    uso = dados.get("usage", {})

    return {
        "provedor": "openai",
        "modelo": modelo,
        "resposta": texto,
        "tempo_segundos": tempo,
        "tokens_entrada": uso.get("prompt_tokens"),
        "tokens_saida": uso.get("completion_tokens"),
        "tokens_total": uso.get("total_tokens"),
        "custo_estimado_usd": None,
        "observacao_custo": (
            "Não calculado: preços por token não "
            "configurados neste projeto."
        )
    }


# ================== FUNCOES DESAFIO 02 ==================
import os
from typing import Any

class LLMAdaptadorMock:
    def __init__(self, nome: str = "mock"):
        self.nome = nome
        self.chamadas = 0
    def completar(self, prompt: str, **kwargs: Any) -> str:
        self.chamadas += 1
        if "Classifique" in prompt: return "inscricao"
        if "Resuma" in prompt: return "Resumo simulado."
        if "entidades" in prompt: return '{"entidades": [], "ausentes": []}'
        if "sentimento" in prompt: return '{"polaridade": "neutra", "justificativa": "Simulado"}'
        return "SEM_EVIDENCIA"

class LLMAdaptadorGemini:
    def __init__(self, modelo: str = "gemini-1.5-flash"):
        self.modelo = modelo
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key: raise ValueError("GEMINI_API_KEY nao configurada")
    def completar(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError("Use Mock offline.")

class LLMAdaptadorOpenAI:
    def __init__(self, modelo: str | None = None):
        load_dotenv(RAIZ / ".env")
        self.modelo = modelo
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key: raise ValueError("OPENAI_API_KEY nao configurada")
    def completar(self, prompt: str, **kwargs: Any) -> str:
        resultado = consultar_llm(
            [{"role": "user", "content": prompt}],
            modelo=self.modelo,
            provedor="openai",
        )
        return resultado["resposta"]

def criar_llm(nome: str = "mock") -> Any:
    if nome.lower() == "mock": return LLMAdaptadorMock()
    if nome.lower() == "gemini": return LLMAdaptadorGemini()
    if nome.lower() == "openai": return LLMAdaptadorOpenAI()
    raise ValueError(f"Provedor desconhecido: {nome}")
