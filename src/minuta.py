import json
import time
import uuid
from pathlib import Path

from src.audit import registrar_execucao
from src.privacidade import minimizar_campos

from src.llm_client import (
    consultar_llm,
    carregar_configuracao,
    ErroLLM
)


RAIZ = Path(__file__).resolve().parent.parent

ORIGEM = RAIZ / "dados" / "processados" / "rf05_extracao.json"
PROMPT = RAIZ / "prompts" / "rf09_minuta_institucional.txt"
DESTINO = RAIZ / "resultados" / "minutas" / "rf09_minuta.txt"
METADADOS = RAIZ / "resultados" / "minutas" / "rf09_informacoes.json"


def preparar_dados(dados):
    """Seleciona somente as informações necessárias à minuta."""

    campos = [
        "protocolo",
        "data",
        "assunto",
        "pedido",
        "categoria",
        "documentos_pendentes",
        "campos_ausentes"
    ]

    return minimizar_campos(dados, campos)


def gerar_minuta(dados, instrucoes):
    if not isinstance(dados, dict):
        raise ValueError("Os dados da solicitação são inválidos.")

    if not isinstance(instrucoes, str) or not instrucoes.strip():
        raise ValueError("O prompt institucional está vazio.")

    dados_protegidos = preparar_dados(dados)

    contexto = {
        "dados_da_solicitacao": dados_protegidos,
        "fontes": [
            "dados/originais/entrada_texto.txt",
            "dados/processados/rf05_extracao.json"
        ]
    }

    resposta = consultar_llm([
        {
            "role": "system",
            "content": instrucoes
        },
        {
            "role": "user",
            "content": (
                "Elabore a minuta com base nestes dados:\n"
                + json.dumps(
                    contexto,
                    ensure_ascii=False,
                    indent=2
                )
            )
        }
    ])

    texto = resposta["resposta"].strip()

    if not texto:
        raise ValueError("A minuta gerada está vazia.")

    return texto, resposta



def registrar_falha_inicial(config, codigo_erro, inicio):
    """Registra falhas anteriores à geração da minuta."""

    auditoria = registrar_execucao({
        "requisito": "RF09",
        "origem": "minuta",
        "provedor": config.get("provedor"),
        "modelo": config.get("modelo"),
        "versao_prompt": "rf09_v1",
        "status": "erro",
        "tempo_segundos": round(
            time.perf_counter() - inicio, 2
        ),
        "revisao_humana": "nao_aplicavel",
        "codigo_erro": codigo_erro
    })

    print("ID de auditoria:", auditoria["id_execucao"])


def salvar_arquivos_com_seguranca(texto_minuta, informacoes):
    """Publica minuta e metadados sem sobrescrever arquivos existentes."""

    import os
    import tempfile

    arquivos_temporarios = []
    publicados = []

    try:
        for destino, conteudo in (
            (DESTINO, texto_minuta),
            (
                METADADOS,
                json.dumps(
                    informacoes,
                    ensure_ascii=False,
                    indent=2
                )
            )
        ):
            destino.parent.mkdir(parents=True, exist_ok=True)

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destino.parent,
                prefix=".rf11_",
                suffix=".tmp",
                delete=False
            ) as temporario:
                temporario.write(conteudo)
                arquivos_temporarios.append(
                    (Path(temporario.name), destino)
                )

        for temporario, destino in arquivos_temporarios:
            # Criação exclusiva: não substitui arquivos existentes.
            with temporario.open("rb") as origem:
                with destino.open("xb") as saida:
                    publicados.append(destino)
                    while True:
                        bloco = origem.read(65536)
                        if not bloco:
                            break
                        saida.write(bloco)

    except OSError:
        for destino in publicados:
            destino.unlink(missing_ok=True)
        raise

    finally:
        for temporario, _ in arquivos_temporarios:
            temporario.unlink(missing_ok=True)

def main():
    inicio_auditoria = time.perf_counter()
    config = carregar_configuracao()

    if config.get("revisao_humana_obrigatoria") is not True:
        registrar_falha_inicial(
            config, "REVISAO_DESABILITADA", inicio_auditoria
        )
        print("Erro: revisão humana obrigatória não habilitada.")
        return

    if config.get("envio_automatico") is not False:
        registrar_falha_inicial(
            config, "ENVIO_AUTOMATICO", inicio_auditoria
        )
        print("Erro: envio automático deve estar desativado.")
        return

    if not ORIGEM.is_file():
        registrar_falha_inicial(
            config, "EXTRACAO_AUSENTE", inicio_auditoria
        )
        print("Erro: extração RF05 não encontrada.")
        return

    if not PROMPT.is_file():
        registrar_falha_inicial(
            config, "PROMPT_AUSENTE", inicio_auditoria
        )
        print("Erro: prompt institucional não encontrado.")
        return

    # Preserva as minutas e os metadados de execuções anteriores.
    if DESTINO.exists() or METADADOS.exists():
        registrar_falha_inicial(
            config, "SAIDA_JA_EXISTENTE", inicio_auditoria
        )
        print(
            "Erro: já existem arquivos de minuta ou metadados. "
            "A execução foi interrompida para evitar sobrescrita."
        )
        return

    try:
        dados = json.loads(
            ORIGEM.read_text(encoding="utf-8-sig")
        )

        # Verifica o vínculo com o caso antes de chamar a IA.
        if not isinstance(dados, dict):
            raise ValueError("Dados da solicitação inválidos.")

        protocolo = dados.get("protocolo")

        if not isinstance(protocolo, str) or not protocolo.strip():
            raise ValueError("Protocolo do caso não encontrado.")

        instrucoes = PROMPT.read_text(encoding="utf-8-sig")

        texto, resposta = gerar_minuta(dados, instrucoes)

        identificador = str(uuid.uuid4())

        informacoes = {
            "requisito": "RF09",
            "id_caso": protocolo,
            "id_execucao": identificador,
            "modalidade_entrada": "texto",
            "arquivo_entrada": "dados/originais/entrada_texto.txt",
            "arquivo_processado": "dados/processados/rf05_extracao.json",
            "arquivo_saida": "resultados/minutas/rf09_minuta.txt",
            "modelo": resposta["modelo"],
            "provedor": resposta["provedor"],
            "tempo_segundos": resposta["tempo_segundos"],
            "tokens_total": resposta["tokens_total"],
            "fontes": [
                "dados/originais/entrada_texto.txt",
                "dados/processados/rf05_extracao.json"
            ],
            "revisao_humana_pendente": True,
            "aprovado": False,
            "enviado": False
        }


        salvar_arquivos_com_seguranca(texto, informacoes)

        try:
            # Rastreabilidade do caso fictício e dos arquivos utilizados.
            auditoria = registrar_execucao({
                "requisito": "RF09",
                "origem": "minuta",
                "id_caso": protocolo,
                "modalidade_entrada": "texto",
                "arquivo_entrada": "dados/originais/entrada_texto.txt",
                "arquivo_processado": "dados/processados/rf05_extracao.json",
                "arquivo_saida": "resultados/minutas/rf09_minuta.txt",
                "provedor": resposta["provedor"],
                "modelo": resposta["modelo"],
                "versao_prompt": "rf09_v1",
                "status": "sucesso",
                "tempo_segundos": round(
                    time.perf_counter() - inicio_auditoria, 2
                ),
                "tokens_entrada": resposta.get("tokens_entrada"),
                "tokens_saida": resposta.get("tokens_saida"),
                "tokens_total": resposta.get("tokens_total"),
                "revisao_humana": "pendente",
                "parametros": {
                    "max_tokens": config["max_tokens"],
                    "thinking_level": "low"
                }
            }, id_execucao=identificador)

        except Exception:
            DESTINO.unlink(missing_ok=True)
            METADADOS.unlink(missing_ok=True)
            raise

        print("ID de auditoria:", auditoria["id_execucao"])
        print("Minuta gerada com sucesso.")
        print("Modelo:", resposta["modelo"])
        print("Tempo:", resposta["tempo_segundos"], "segundos")
        print("Tokens totais:", resposta["tokens_total"])
        print("Arquivo:", DESTINO)
        print("Status: PENDENTE DE REVISÃO HUMANA")
        print("Envio automático: DESATIVADO")

    except (ErroLLM, ValueError, json.JSONDecodeError, OSError) as erro:
        codigo = (
            "ERRO_LLM" if isinstance(erro, ErroLLM)
            else "ERRO_GRAVACAO" if isinstance(erro, OSError)
            else "ERRO_DADOS"
        )

        auditoria = registrar_execucao({
            "requisito": "RF09",
            "origem": "minuta",
            "provedor": config.get("provedor"),
            "modelo": config.get("modelo"),
            "versao_prompt": "rf09_v1",
            "status": "erro",
            "tempo_segundos": round(
                time.perf_counter() - inicio_auditoria, 2
            ),
            "revisao_humana": "nao_aplicavel",
            "codigo_erro": codigo
        })

        print("ID de auditoria:", auditoria["id_execucao"])
        print("Erro ao gerar minuta:", erro)


if __name__ == "__main__":
    main()
