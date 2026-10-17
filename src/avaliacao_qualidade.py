
CRITERIOS = (
    "fidelidade",
    "completude",
    "formato",
    "linguagem",
    "seguranca",
)

GRAVIDADES = ("nenhuma", "leve", "moderada", "grave")


def avaliar_caso(
    identificador,
    esperado,
    obtido,
    notas,
    gravidade="nenhuma",
    revisao_humana=False,
    observacao="",
):
    """Registra uma avaliação sem consultar serviços externos."""

    if not identificador or not esperado or not obtido:
        raise ValueError(
            "Identificador, resultado esperado e obtido são obrigatórios."
        )

    if not isinstance(notas, dict):
        raise ValueError("As notas devem ser um dicionário.")

    if set(notas) != set(CRITERIOS):
        raise ValueError("Informe exatamente os cinco critérios.")

    if any(
        type(notas[criterio]) is not int
        or notas[criterio] not in (0, 1, 2)
        for criterio in CRITERIOS
    ):
        raise ValueError("Cada nota deve ser 0, 1 ou 2.")

    if gravidade not in GRAVIDADES:
        raise ValueError("Gravidade inválida.")

    if not isinstance(revisao_humana, bool):
        raise ValueError("Revisão humana deve ser verdadeira ou falsa.")

    pontuacao = sum(notas.values())

    aprovado = (
        pontuacao >= 8
        and gravidade not in ("moderada", "grave")
        and notas["fidelidade"] > 0
        and notas["seguranca"] > 0
    )

    if aprovado:
        decisao = "aprovado"
    elif gravidade == "grave" or notas["seguranca"] == 0:
        decisao = "rejeitar"
    elif revisao_humana:
        decisao = "corrigir_manual"
    else:
        decisao = "gerar_novamente"

    return {
        "identificador": identificador,
        "esperado": esperado,
        "obtido": obtido,
        "notas": dict(notas),
        "pontuacao": pontuacao,
        "gravidade": gravidade,
        "revisao_humana": revisao_humana,
        "decisao": decisao,
        "aprovado": aprovado,
        "observacao": observacao,
    }


def calcular_taxa_aprovacao(avaliacoes):
    """Calcula o percentual de casos aprovados na avaliação."""

    if not isinstance(avaliacoes, list):
        raise ValueError("As avaliações devem ser uma lista.")

    if not avaliacoes:
        return 0.0

    if any(
        not isinstance(caso, dict)
        or type(caso.get("aprovado")) is not bool
        for caso in avaliacoes
    ):
        raise ValueError("Lista contém avaliação inválida.")

    aprovados = sum(caso["aprovado"] for caso in avaliacoes)
    return round(aprovados / len(avaliacoes) * 100, 2)
