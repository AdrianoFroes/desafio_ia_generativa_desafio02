"""Regressão das correções finais de evidência, sem acesso a APIs."""
import hashlib
import json
from pathlib import Path
from src import demonstracao

ROOT = Path(__file__).resolve().parents[1]


def test_demonstracao_usa_audio_definitivo():
    arquivos = [x[1] for x in demonstracao.ETAPAS]
    assert 'resultados/audios/rf07_minuta_rf09_aprovada.wav' in arquivos
    assert 'resultados/audios/rf07_revisao_humana.json' in arquivos
    assert 'resultados/logs/auditoria.jsonl' in arquivos


def test_revisao_audio_final_corresponde_a_minuta():
    base = ROOT / 'resultados/audios'
    dados = json.loads((base / 'rf07_minuta_rf09_informacoes.json').read_text(encoding='utf-8-sig'))
    revisao = json.loads((base / 'rf07_revisao_humana.json').read_text(encoding='utf-8-sig'))
    assert dados['sha256_minuta_aprovada'] == hashlib.sha256((ROOT / 'resultados/minutas/rf09_minuta_revisada.txt').read_bytes()).hexdigest()
    assert revisao['revisao_humana']['resultado'] == 'aprovado'
    assert revisao['revisao_humana']['realizada'] is True
    assert (base / 'rf07_minuta_rf09_aprovada.wav').is_file()
    # A geração precede a escuta; não alterar o estado histórico.
    assert dados['revisao_audio_pendente'] is True


def test_log_real_vinculado_e_gabarito_retroativo():
    base = ROOT / 'resultados'
    dados = json.loads((base / 'audios/rf07_minuta_rf09_informacoes.json').read_text(encoding='utf-8-sig'))
    linhas = (base / 'logs/auditoria.jsonl').read_text(encoding='utf-8-sig').splitlines()
    assert any(json.loads(l).get('id_execucao') == dados['id_execucao'] for l in linhas if l.strip())
    origem = json.loads((ROOT / 'dados/gabaritos/rf06_referencia_origem.json').read_text(encoding='utf-8-sig'))
    assert origem['independente'] is False
