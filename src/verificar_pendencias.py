"""Verifica evid?ncias reais sem inventar hist?rico."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

from src.audit import listar_execucoes, consultar_revisao_humana

RAIZ = Path(__file__).resolve().parent.parent


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def ler_json(caminho):
    return json.loads(caminho.read_text(encoding="utf-8-sig"))


def sha256(caminho):
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def verificar():
    # RF07: preservar a verifica??o existente do ?udio definitivo.
    audios = RAIZ / "resultados/audios"
    minuta = RAIZ / "resultados/minutas/rf09_minuta_revisada.txt"
    audio = audios / "rf07_minuta_rf09_aprovada.wav"
    info07 = audios / "rf07_minuta_rf09_informacoes.json"
    revisao07 = audios / "rf07_revisao_humana.json"

    for caminho in (minuta, audio, info07, revisao07):
        exigir(caminho.is_file(), f"RF07: arquivo ausente: {caminho.relative_to(RAIZ)}")

    dados07 = ler_json(info07)
    aprovacao07 = ler_json(revisao07)

    exigir(
        dados07.get("sha256_minuta_aprovada") == sha256(minuta),
        "RF07: hash da minuta n?o confere."
    )
    exigir(
        aprovacao07.get("arquivo_audio") == "resultados/audios/rf07_minuta_rf09_aprovada.wav",
        "RF07: ?udio aprovado divergente."
    )
    exigir(
        aprovacao07.get("arquivo_texto") == "resultados/minutas/rf09_minuta_revisada.txt",
        "RF07: minuta aprovada divergente."
    )
    rev07 = aprovacao07.get("revisao_humana", {})
    exigir(
        rev07.get("realizada") is True
        and rev07.get("resultado") == "aprovado"
        and rev07.get("data_registro"),
        "RF07: aprova??o humana n?o comprovada."
    )
    print("RF07 OK: ?udio definitivo, hash e aprova??o humana conferidos.")

    log = RAIZ / "resultados/logs/auditoria.jsonl"
    exigir(log.is_file(), "RF11: arquivo central de auditoria ausente.")
    registros = listar_execucoes(log)

    def obter_execucao(id_execucao, requisito):
        eventos = [
            r for r in registros
            if r.get("id_execucao") == id_execucao
            and r.get("requisito") == requisito
            and r.get("tipo_evento", "execucao") == "execucao"
            and r.get("status") == "sucesso"
        ]
        exigir(
            len(eventos) == 1,
            f"{requisito}: evento de execu??o ausente ou duplicado."
        )
        return eventos[0]

    # RF06: refer?ncia confirmada antes da nova infer?ncia,
    # mas originada de uma transcri??o anterior.
    gabarito06 = RAIZ / "dados/gabaritos/rf06_gabarito_validado.txt"
    origem06 = RAIZ / "dados/gabaritos/rf06_gabarito_validado_origem.json"
    audio06 = RAIZ / "dados/originais/entrada_audio.mp3"
    texto06 = RAIZ / "dados/processados/rf06_nova_transcricao_20261017_160731.txt"
    info06 = RAIZ / "dados/processados/rf06_nova_transcricao_20261017_160731_informacoes.json"

    for caminho in (gabarito06, origem06, audio06, texto06, info06):
        exigir(caminho.is_file(), f"RF06: arquivo ausente: {caminho.relative_to(RAIZ)}")

    meta06 = ler_json(origem06)
    dados06 = ler_json(info06)
    exigir(meta06.get("validado_antes_da_nova_execucao") is True,
           "RF06: valida??o pr?via n?o est? registrada.")
    exigir(meta06.get("sha256_audio") == sha256(audio06),
           "RF06: hash do ?udio original n?o confere.")
    exigir(meta06.get("gabarito") == "dados/gabaritos/rf06_gabarito_validado.txt",
           "RF06: caminho do gabarito n?o confere.")

    evento06 = obter_execucao(dados06.get("id_execucao"), "RF06")
    exigir(
        datetime.fromisoformat(meta06["data_hora_validacao_registrada"])
        < datetime.fromisoformat(evento06["data_hora"]),
        "RF06: a valida??o n?o antecede a nova execu??o."
    )
    exigir(
        consultar_revisao_humana(dados06["id_execucao"], log) == "aprovado",
        "RF06: aprova??o humana n?o confirmada na auditoria."
    )
    print("RF06 OK: nova transcri??o aprovada e refer?ncia confirmada antes da nova execu??o.")
    print("RF06 LIMITA??O: a refer?ncia deriva de transcri??o anterior; n?o ? independente da primeira infer?ncia.")

    # RF08: gabarito visual definido antes da nova execu??o.
    pdf08 = RAIZ / "dados/originais/entrada_pdf-imagem.pdf"
    gabarito08 = RAIZ / "dados/gabaritos/rf08_gabarito_validado.json"
    origem08 = RAIZ / "dados/gabaritos/rf08_gabarito_validado_origem.json"
    bruto08 = RAIZ / "dados/processados/rf08_nova_extracao_20261017_161929.txt"
    corrigido08 = RAIZ / "dados/processados/rf08_nova_extracao_20261017_161929_corrigida.txt"
    info08 = RAIZ / "dados/processados/rf08_nova_extracao_20261017_161929_informacoes.json"

    for caminho in (pdf08, gabarito08, origem08, bruto08, corrigido08, info08):
        exigir(caminho.is_file(), f"RF08: arquivo ausente: {caminho.relative_to(RAIZ)}")

    meta08 = ler_json(origem08)
    campos08 = ler_json(gabarito08)
    dados08 = ler_json(info08)

    exigir(meta08.get("validado_antes_da_nova_execucao") is True,
           "RF08: valida??o pr?via n?o est? registrada.")
    exigir(meta08.get("sha256_documento") == sha256(pdf08),
           "RF08: hash do PDF original n?o confere.")
    exigir(len(campos08) == 6 and len(meta08.get("campos_confirmados", [])) == 6,
           "RF08: quantidade de campos confirmados inesperada.")

    evento08 = obter_execucao(dados08.get("id_execucao"), "RF08")
    exigir(
        datetime.fromisoformat(meta08["data_hora_registro"])
        < datetime.fromisoformat(evento08["data_hora"]),
        "RF08: o gabarito visual n?o antecede a nova execu??o."
    )
    exigir(
        consultar_revisao_humana(dados08["id_execucao"], log) == "aprovado",
        "RF08: aprova??o humana n?o confirmada na auditoria."
    )

    evento_decisao08 = [
        r for r in registros
        if r.get("tipo_evento") == "decisao_humana"
        and r.get("id_execucao_referenciada") == dados08["id_execucao"]
    ]
    exigir(len(evento_decisao08) == 1,
           "RF08: evento de aprova??o ausente ou duplicado.")
    exigir(
        evento_decisao08[0].get("arquivo_revisado")
        == "dados/processados/rf08_nova_extracao_20261017_161929_corrigida.txt",
        "RF08: aprova??o n?o aponta para o arquivo corrigido."
    )
    exigir(
        evento_decisao08[0].get("sha256_documento") == sha256(corrigido08),
        "RF08: hash do arquivo corrigido n?o confere."
    )
    print("RF08 OK: seis campos de refer?ncia pr?via, extra??o nova e revis?o corrigida aprovada.")
    print("RF08 LIMITA??O: as corre??es humanas posteriores n?o contam como acertos originais do OCR.")

    # RF11: mostrar o n?mero real de eventos, sem reconstruir o passado.
    print(f"RF11 PARCIAL: {len(registros)} eventos reais no hist?rico central; hist?rico anterior incompleto.")
    print("Verifica??o conclu?da. Nenhum registro de auditoria foi criado ou alterado.")


if __name__ == "__main__":
    verificar()
