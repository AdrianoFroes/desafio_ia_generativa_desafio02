"""Roteiro offline do fluxo multimodal: verifica evidências sem fingir novas chamadas à IA."""
import argparse
from pathlib import Path
from src.audit import registrar_execucao, listar_execucoes

RAIZ = Path(__file__).resolve().parent.parent
ETAPAS = [
    ('Entrada textual', 'dados/originais/entrada_texto.txt'),
    ('Extração RF05', 'dados/processados/rf05_extracao.json'),
    ('Áudio de entrada RF06', 'dados/originais/entrada_audio.mp3'),
    ('Transcrição RF06', 'dados/processados/rf06_transcricao_revisada.txt'),
    ('Síntese de voz RF07', 'resultados/audios/rf07_minuta_falada.wav'),
    ('Documento original RF08', 'dados/originais/entrada_pdf-imagem.pdf'),
    ('OCR e revisão RF08', 'dados/processados/rf08_texto_corrigido.txt'),
    ('Comparação RF08', 'dados/processados/rf08_comparacao.json'),
    ('Minuta revisada RF09', 'resultados/minutas/rf09_minuta_revisada.txt'),
    ('Minuta com brasão RF09', 'resultados/minutas/rf09_minuta_revisada_com_brasao.pdf'),
    ('Imagem revisada RF10', 'resultados/imagens/rf10_cartaz_matricula_revisado.png'),
    ('Avaliação RF13', 'resultados/logs/rf13_avaliacao.json'),
]

def main():
    parser = argparse.ArgumentParser(description='Demonstra evidências existentes sem usar APIs.')
    parser.add_argument('--registrar', action='store_true', help='Registra somente a execução desta conferência offline.')
    args = parser.parse_args()
    print('DEMONSTRAÇÃO OFFLINE — NÃO EXECUTA NOVAS INFERÊNCIAS')
    ausentes = []
    for titulo, relativo in ETAPAS:
        existe = (RAIZ / relativo).is_file()
        print(f'{"OK" if existe else "AUSENTE"}: {titulo} — {relativo}')
        if not existe:
            ausentes.append(relativo)
    if args.registrar:
        registro = registrar_execucao({
            'requisito': 'RF11', 'origem': 'demonstracao',
            'provedor': 'local', 'modelo': 'sem_api', 'versao_prompt': 'nao_aplicavel',
            'status': 'erro' if ausentes else 'sucesso',
            'revisao_humana': 'nao_aplicavel',
            'modalidade_entrada': 'texto',
            'arquivo_saida': 'resultados/logs/demonstracao_offline.jsonl',
        }, caminho=RAIZ / 'resultados/logs/demonstracao_offline.jsonl')
        print('Auditoria da conferência offline:', registro['id_execucao'])
    print('Atenção: evidências preexistentes; não comprova uma execução ponta a ponta.')
    if ausentes:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
