"""Gera cópias de apresentação em PDF das minutas existentes, sem API nem envio.

O texto original permanece intacto. A imagem institucional é incluída apenas
no documento de apresentação, sem implicar chancela oficial.
"""
from pathlib import Path
import argparse
import pymupdf

RAIZ = Path(__file__).resolve().parent.parent
BRASAO = RAIZ / 'dados/originais/brasao.png'
PASTA = RAIZ / 'resultados/minutas'


def gerar_pdf(versao='revisada'):
    if versao not in ('original', 'revisada'):
        raise ValueError('Versão inválida')
    nome = 'rf09_minuta_revisada' if versao == 'revisada' else 'rf09_minuta'
    entrada = PASTA / f'{nome}.txt'
    saida = PASTA / f'{nome}_com_brasao.pdf'
    if not BRASAO.is_file() or not entrada.is_file():
        raise FileNotFoundError('Brasão ou minuta de origem não encontrado')
    texto = entrada.read_text(encoding='utf-8-sig')
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    y = 32
    margem = 55
    def nova_pagina():
        nonlocal page, y
        page = doc.new_page(width=595, height=842)
        y = 52
    page.insert_image(pymupdf.Rect(267, y, 328, y + 58), filename=str(BRASAO), keep_proportion=True)
    y += 67
    page.insert_text((margem, y), 'DOCUMENTO FICTÍCIO — PROTÓTIPO ACADÊMICO', fontsize=10, fontname='hebo')
    y += 17
    page.insert_text((margem, y), 'NÃO É COMUNICAÇÃO OFICIAL — NÃO ENVIAR', fontsize=9, color=(0.6, 0.1, 0.1))
    y += 28
    largura = 595 - 2*margem
    for linha in texto.splitlines():
        if not linha.strip():
            y += 11
            continue
        # quebra de linhas proporcional usando métrica de fonte do próprio PDF
        palavras = linha.split()
        partes = []
        atual = ''
        for palavra in palavras:
            candidato = (atual + ' ' + palavra).strip()
            if pymupdf.get_text_length(candidato, fontname='helv', fontsize=10) > largura and atual:
                partes.append(atual)
                atual = palavra
            else:
                atual = candidato
        if atual:
            partes.append(atual)
        for parte in partes:
            if y > 775:
                nova_pagina()
            page.insert_text((margem, y), parte, fontname='helv', fontsize=10)
            y += 14
    if saida.exists():
        saida.unlink()
    doc.save(saida)
    doc.close()
    return saida


def main():
    parser = argparse.ArgumentParser(description='Gera minuta PDF com brasão (sem API).')
    parser.add_argument('--versao', choices=('original', 'revisada', 'ambas'), default='ambas')
    args = parser.parse_args()
    for versao in ('original', 'revisada') if args.versao == 'ambas' else (args.versao,):
        print('PDF criado:', gerar_pdf(versao))


if __name__ == '__main__':
    main()
