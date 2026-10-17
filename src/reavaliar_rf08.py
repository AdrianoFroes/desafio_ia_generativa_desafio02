import hashlib
import json
import time
import uuid
from datetime import datetime
from pathlib import Path

from src.audit import registrar_execucao
from src.vision import RAIZ, MODELO, extrair_documento


def main():
    origem = RAIZ / "dados/originais/entrada_pdf-imagem.pdf"
    gabarito = RAIZ / "dados/gabaritos/rf08_gabarito_validado.json"
    metadados = RAIZ / "dados/gabaritos/rf08_gabarito_validado_origem.json"
    destino = RAIZ / "dados/processados"

    for arquivo in (origem, gabarito, metadados):
        if not arquivo.is_file():
            raise FileNotFoundError(f"Arquivo necessário não encontrado: {arquivo}")

    referencia = json.loads(gabarito.read_text(encoding="utf-8"))
    validacao = json.loads(metadados.read_text(encoding="utf-8"))

    if not validacao.get("validado_antes_da_nova_execucao"):
        raise ValueError("O gabarito não está marcado como validado previamente.")

    if len(referencia) != 6:
        raise ValueError("O gabarito deve conter os seis campos confirmados.")

    hash_pdf = hashlib.sha256(origem.read_bytes()).hexdigest()

    if hash_pdf != validacao.get("sha256_documento"):
        raise ValueError("O PDF original foi alterado após a validação humana.")

    id_execucao = str(uuid.uuid4())
    momento = datetime.now().strftime("%Y%m%d_%H%M%S")

    nome_base = f"rf08_nova_extracao_{momento}"
    arquivo_texto = destino / f"{nome_base}.txt"
    arquivo_info = destino / f"{nome_base}_informacoes.json"

    if arquivo_texto.exists() or arquivo_info.exists():
        raise FileExistsError("Arquivos de destino já existem.")

    inicio = time.perf_counter()

    resultado = extrair_documento(origem)

    informacoes = {
        chave: valor
        for chave, valor in resultado.items()
        if chave != "texto_bruto"
    }

    informacoes.update({
        "id_execucao": id_execucao,
        "gabarito_validado": "dados/gabaritos/rf08_gabarito_validado.json",
        "sha256_documento_original": hash_pdf,
        "data_hora_execucao": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
    })

    destino.mkdir(parents=True, exist_ok=True)

    arquivos_criados = []

    try:
        with arquivo_texto.open("x", encoding="utf-8") as arquivo:
            arquivos_criados.append(arquivo_texto)
            arquivo.write(resultado["texto_bruto"])

        with arquivo_info.open("x", encoding="utf-8") as arquivo:
            arquivos_criados.append(arquivo_info)
            json.dump(informacoes, arquivo, ensure_ascii=False, indent=2)

        registrar_execucao(
            {
                "requisito": "RF08",
                "origem": "vision",
                "provedor": "google",
                "modelo": resultado["modelo"],
                "versao_prompt": "rf08_v1",
                "parametros": {},
                "modalidade_entrada": "imagem",
                "arquivo_entrada": "dados/originais/entrada_pdf-imagem.pdf",
                "arquivo_saida": arquivo_texto.relative_to(RAIZ).as_posix(),
                "arquivo_processado": arquivo_info.relative_to(RAIZ).as_posix(),
                "status": "sucesso",
                "tempo_segundos": round(time.perf_counter() - inicio, 2),
                "tokens_entrada": resultado.get("tokens_entrada"),
                "tokens_saida": resultado.get("tokens_saida"),
                "tokens_total": resultado.get("tokens_total"),
                "revisao_humana": "pendente",
            },
            id_execucao=id_execucao,
        )

    except Exception:
        for arquivo in arquivos_criados:
            arquivo.unlink(missing_ok=True)
        raise

    print("Nova extração OCR realizada com sucesso.")
    print("ID:", id_execucao)
    print("Modelo:", resultado["modelo"])
    print("Texto bruto:", arquivo_texto)
    print("Informações:", arquivo_info)
    print("Revisão humana: pendente")


if __name__ == "__main__":
    main()
