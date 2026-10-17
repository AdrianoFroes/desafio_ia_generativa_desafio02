import base64
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


RAIZ = Path(__file__).resolve().parent.parent
MODELO = "gemini-3.5-transcribe"


def transcrever_audio(caminho, modelo=MODELO, timeout=180):
    load_dotenv(RAIZ / ".env")
    chave = os.getenv("GEMINI_API_KEY")

    if not chave:
        raise ValueError("Chave GEMINI_API_KEY não encontrada.")

    caminho = Path(caminho)

    if not caminho.is_file():
        raise FileNotFoundError("Arquivo de áudio não encontrado.")

    if caminho.suffix.lower() != ".mp3":
        raise ValueError("O arquivo deve estar no formato MP3.")

    audio_base64 = base64.b64encode(caminho.read_bytes()).decode("ascii")

    corpo = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Transcreva fielmente este áudio em português. "
                            "Não resuma, não invente informações e não "
                            "adicione comentários. Retorne somente a transcrição."
                        )
                    },
                    {
                        "inline_data": {
                            "mime_type": "audio/mpeg",
                            "data": audio_base64
                        }
                    }
                ]
            }
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
        raise RuntimeError("A consulta demorou mais que o esperado.") from erro
    except requests.RequestException as erro:
        raise RuntimeError("Não foi possível conectar ao Gemini.") from erro

    tempo = round(time.perf_counter() - inicio, 2)

    if resposta.status_code != 200:
        erros = {
            400: "Formato da requisição não aceito.",
            401: "Chave de acesso inválida.",
            403: "Acesso não permitido.",
            404: "Modelo não encontrado ou indisponível.",
            413: "Arquivo muito grande.",
            429: "Limite de uso atingido.",
            500: "Erro interno do provedor.",
            503: "Serviço temporariamente indisponível."
        }
        mensagem = erros.get(resposta.status_code, "Falha na API.")
        raise RuntimeError(f"{mensagem} HTTP {resposta.status_code}.")

    try:
        dados = resposta.json()
    except ValueError as erro:
        raise RuntimeError("Resposta inválida da API.") from erro

    partes = []

    for candidato in dados.get("candidates", []):
        for parte in candidato.get("content", {}).get("parts", []):
            if isinstance(parte.get("text"), str):
                partes.append(parte["text"])

            audio_transcricao = parte.get("audioTranscription")

            if isinstance(audio_transcricao, str):
                partes.append(audio_transcricao)

            elif isinstance(audio_transcricao, dict):
                texto_audio = audio_transcricao.get("text")

                if isinstance(texto_audio, str):
                    partes.append(texto_audio)

    transcricao = "\n".join(partes).strip()

    if not transcricao:
        candidatos = dados.get("candidates", [])

        motivos = [
            candidato.get("finishReason", "não informado")
            for candidato in candidatos
        ]

        bloqueio = dados.get("promptFeedback", {}).get(
            "blockReason", "não informado"
        )

        raise RuntimeError(
            "A API não retornou uma transcrição. "
            f"Motivos de finalização: {motivos}. "
            f"Motivo de bloqueio: {bloqueio}. "
            f"Quantidade de candidatos: {len(candidatos)}."
        )

    uso = dados.get("usageMetadata", {})

    return {
        "modelo": modelo,
        "transcricao": transcricao,
        "tempo_segundos": tempo,
        "tokens_entrada": uso.get("promptTokenCount"),
        "tokens_saida": uso.get("candidatesTokenCount"),
        "tokens_total": uso.get("totalTokenCount"),
        "revisao_humana": True
    }


def main():
    origem = RAIZ / "dados" / "originais" / "entrada_audio.mp3"
    pasta = RAIZ / "dados" / "processados"

    try:
        resultado = transcrever_audio(origem)

        pasta.mkdir(parents=True, exist_ok=True)

        arquivo_texto = pasta / "rf06_transcricao.txt"
        arquivo_info = pasta / "rf06_informacoes.json"

        arquivo_texto.write_text(
            resultado["transcricao"], encoding="utf-8"
        )

        informacoes = {
            chave: valor
            for chave, valor in resultado.items()
            if chave != "transcricao"
        }

        arquivo_info.write_text(
            json.dumps(informacoes, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print("Transcrição realizada com sucesso.")
        print("Modelo:", resultado["modelo"])
        print("Tempo:", resultado["tempo_segundos"], "segundos")
        print("Tokens totais:", resultado["tokens_total"])
        print("Caracteres transcritos:", len(resultado["transcricao"]))
        print("Arquivo:", arquivo_texto)
        print("Revisão humana obrigatória:", resultado["revisao_humana"])

    except (ValueError, FileNotFoundError, RuntimeError) as erro:
        print("Erro:", erro)


if __name__ == "__main__":
    main()
