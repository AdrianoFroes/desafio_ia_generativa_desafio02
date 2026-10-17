import json
import time
import uuid
from datetime import datetime
from pathlib import Path

from src.audio import RAIZ, MODELO, transcrever_audio
from src.audit import registrar_execucao

def main():
    origem = RAIZ / "dados/originais/entrada_audio.mp3"
    gabarito = RAIZ / "dados/gabaritos/rf06_gabarito_validado.txt"
    metadados_gabarito = RAIZ / "dados/gabaritos/rf06_gabarito_validado_origem.json"

    pasta = RAIZ / "dados/processados"
    identificador = str(uuid.uuid4())
    sufixo = datetime.now().strftime("%Y%m%d_%H%M%S")

    nome_texto = f"rf06_nova_transcricao_{sufixo}.txt"
    nome_info = f"rf06_nova_transcricao_{sufixo}_informacoes.json"

    arquivo_texto = pasta / nome_texto
    arquivo_info = pasta / nome_info

    if not origem.is_file():
        raise FileNotFoundError("Áudio original não encontrado.")

    if not gabarito.is_file() or not metadados_gabarito.is_file():
        raise FileNotFoundError("Gabarito validado não encontrado.")

    dados_gabarito = json.loads(metadados_gabarito.read_text(encoding="utf-8"))

    if not dados_gabarito.get("validado_antes_da_nova_execucao"):
        raise ValueError("Gabarito não validado para nova execução.")

    if arquivo_texto.exists() or arquivo_info.exists():
        raise FileExistsError("Arquivos de destino já existem.")

    inicio = time.perf_counter()

    auditoria = {
        "requisito": "RF06",
        "origem": "reavaliar_rf06",
        "provedor": "google",
        "modelo": MODELO,
        "versao_prompt": "rf06_v1",
        "parametros": {},
        "id_caso": "rf06_reavaliacao",
        "modalidade_entrada": "audio",
        "arquivo_entrada": "dados/originais/entrada_audio.mp3",
        "arquivo_saida": f"dados/processados/{nome_texto}",
        "arquivo_processado": f"dados/processados/{nome_info}",
        "revisao_humana": "pendente",
    }

    try:
        resultado = transcrever_audio(origem)

        informacoes = {
            chave: valor
            for chave, valor in resultado.items()
            if chave != "transcricao"
        }

        informacoes["id_execucao"] = identificador
        informacoes["gabarito"] = "dados/gabaritos/rf06_gabarito_validado.txt"
        informacoes["revisao_humana_pendente"] = True

        pasta.mkdir(parents=True, exist_ok=True)

        with arquivo_texto.open("x", encoding="utf-8") as arquivo:
            arquivo.write(resultado["transcricao"])

        with arquivo_info.open("x", encoding="utf-8") as arquivo:
            json.dump(informacoes, arquivo, ensure_ascii=False, indent=2)

        auditoria.update({
            "status": "sucesso",
            "tempo_segundos": round(time.perf_counter() - inicio, 2),
            "tokens_entrada": resultado.get("tokens_entrada"),
            "tokens_saida": resultado.get("tokens_saida"),
            "tokens_total": resultado.get("tokens_total"),
        })

        registrar_execucao(auditoria, id_execucao=identificador)

        print("Nova transcrição realizada com sucesso.")
        print("ID:", identificador)
        print("Transcrição:", arquivo_texto)
        print("Informações:", arquivo_info)
        print("Revisão humana: pendente")

    except Exception as erro:
        auditoria.update({
            "status": "erro",
            "tempo_segundos": round(time.perf_counter() - inicio, 2),
            "codigo_erro": "ERRO_REAVALIACAO",
        })

        registrar_execucao(auditoria, id_execucao=identificador)
        print("Erro:", erro)
        raise

if __name__ == "__main__":
    main()
