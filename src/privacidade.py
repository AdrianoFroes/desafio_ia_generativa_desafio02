
import re


def minimizar_texto(texto):
    """
    Oculta padrões conhecidos de dados pessoais antes
    do envio de textos fictícios ao provedor de IA.

    Não substitui a revisão humana.
    """
    if not isinstance(texto, str):
        raise ValueError("O conteúdo deve ser um texto.")

    regras = [
        (
            r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
            "[CPF ocultado]",
        ),
        (
            r"\b\d{11}\b",
            "[CPF ocultado]",
        ),
        (
            r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
            "[e-mail ocultado]",
        ),
        (
            r"\b(?:\+55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b",
            "[telefone ocultado]",
        ),
        (
            r"\bCPF\s*[:\-]?\s*[\d.\-]+",
            "[CPF ocultado]",
        ),
        (
            r"\bRG\s*[:\-]?\s*[\d.\-]+",
            "[RG ocultado]",
        ),
        (
            r"\bnasci em\s+\d{2}/\d{2}/\d{4}\b",
            "[data de nascimento ocultada]",
        ),
        (
            r"\bnome da mãe\s*[:,]?\s*[^;\n.]+",
            "[nome da mãe ocultado]",
        ),
        (
            r"\bmeu nome é\s+[^,;\n.]+",
            "meu nome é [solicitante]",
        ),
    ]

    resultado = texto

    for padrao, substituicao in regras:
        resultado = re.sub(
            padrao,
            substituicao,
            resultado,
            flags=re.IGNORECASE,
        )

    return resultado


def minimizar_campos(dados, campos_permitidos):
    """
    Seleciona apenas campos autorizados e minimiza
    valores textuais, sem modificar o dicionário original.
    """
    if not isinstance(dados, dict):
        raise ValueError("Os dados devem ser um dicionário.")

    resultado = {}

    for campo in campos_permitidos:
        valor = dados.get(campo, "não localizado")

        if isinstance(valor, str):
            resultado[campo] = minimizar_texto(valor)
        elif isinstance(valor, list):
            resultado[campo] = [
                minimizar_texto(item)
                if isinstance(item, str)
                else item
                for item in valor
            ]
        else:
            resultado[campo] = valor

    return resultado
