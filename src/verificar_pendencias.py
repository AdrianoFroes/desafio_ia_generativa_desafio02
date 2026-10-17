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
    print("RF06: referência posterior NÃO é gabarito independente; conferir áudio original.")
    print("RF08: gabarito final revisto após OCR; não é avaliação cega.")
    if not (audio.exists() and info.exists()):
        print("RF07 PENDENTE: sintetizar minuta RF09 aprovada e revisar áudio por escuta.")
    else:
        dados = json.loads(info.read_text(encoding="utf-8"))
        esperado = hashlib.sha256(minuta.read_bytes()).hexdigest()
        if dados.get("sha256_minuta_aprovada") != esperado:
            raise ValueError("RF07: hash da minuta não corresponde ao texto atual!")
        print("RF07: áudio presente e hash da minuta confere; revisão por escuta:", "PENDENTE" if dados.get("revisao_audio_pendente", True) else "DECLARADA")
    log = RAIZ / "resultados" / "logs" / "auditoria.jsonl"
    print("RF11: histórico central", "encontrado" if log.exists() else "ausente; não criar logs retroativos")

if __name__ == "__main__":
    verificar()
