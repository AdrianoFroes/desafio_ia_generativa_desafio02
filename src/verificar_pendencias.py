"""Verifica evidências existentes sem inferência ou falsificação de logs."""
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

def verificar():
    audios = RAIZ / "resultados" / "audios"
    minuta = RAIZ / "resultados" / "minutas" / "rf09_minuta_revisada.txt"
    audio = audios / "rf07_minuta_rf09_aprovada.wav"
    info = audios / "rf07_minuta_rf09_informacoes.json"
    revisao = audios / "rf07_revisao_humana.json"
    print("RF06 RESSALVA: referência produzida após a inferência; não é gabarito prévio independente.")
    print("RF08 RESSALVA: gabarito final ajustado após OCR; comparação retrospectiva.")
    if not all(x.is_file() for x in (minuta, audio, info, revisao)):
        raise SystemExit("RF07 PENDENTE: faltam áudio final, minuta, metadados ou aprovação humana.")
    dados = json.loads(info.read_text(encoding="utf-8-sig"))
    aprovado = json.loads(revisao.read_text(encoding="utf-8-sig"))
    esperado = hashlib.sha256(minuta.read_bytes()).hexdigest()
    if dados.get("sha256_minuta_aprovada") != esperado:
        raise ValueError("RF07: hash da minuta difere do texto usado na síntese!")
    if aprovado.get("arquivo_audio") != "resultados/audios/rf07_minuta_rf09_aprovada.wav":
        raise ValueError("RF07: a aprovação se refere a outro áudio!")
    if aprovado.get("arquivo_texto") != "resultados/minutas/rf09_minuta_revisada.txt":
        raise ValueError("RF07: a aprovação se refere a outra minuta!")
    rev = aprovado.get("revisao_humana", {})
    if rev.get("realizada") is not True or rev.get("resultado") != "aprovado" or not rev.get("data_registro"):
        raise ValueError("RF07: revisão humana não comprovada!")
    print("RF07 OK: arquivo final presente, hash da minuta confirmado e revisão humana posterior aprovada.")
    log = RAIZ / "resultados" / "logs" / "auditoria.jsonl"
    if not log.is_file():
        print("RF11 PARCIAL: nenhum registro real central disponível.")
        return
    registros = [json.loads(l) for l in log.read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    vinculo = [r for r in registros if r.get("id_execucao") == dados.get("id_execucao") and r.get("requisito") == "RF07"]
    if not vinculo:
        raise ValueError("RF11: registro de execução do áudio final não localizado!")
    print(f"RF11 PARCIAL: {len(registros)} evento(s) real(is) central(is), incluindo RF07; histórico anterior incompleto.")

if __name__ == "__main__":
    verificar()
