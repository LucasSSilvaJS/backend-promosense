"""Períodos Double Date (Shopee) e aspectos de análise."""

from app.constants.dataset import ANO_FIM, ANO_INICIO

# Edições Double Date por ano de coleta (2024–2026)
PERIODOS_PROMOCIONAIS: dict[str, dict] = {
    f"double_date_{ano}": {
        "label": f"Double Date {ano}",
        "ano": ano,
        "meses": tuple(range(1, 13)),
        "descricao": (
            f"Avaliações coletadas na Shopee durante campanhas Double Date em {ano}."
        ),
    }
    for ano in range(ANO_INICIO, ANO_FIM + 1)
}

PERIODOS_ORDEM = list(PERIODOS_PROMOCIONAIS.keys())

ASPECTOS = ("preco", "entrega", "qualidade")

ASPECTO_LABELS = {
    "preco": "Preço",
    "entrega": "Entrega",
    "qualidade": "Qualidade",
}

ASPECTO_KEYWORDS: dict[str, list[str]] = {
    "entrega": [
        "entrega",
        "prazo",
        "frete",
        "envio",
        "atras",
        "chegou",
        "recebi",
        "logística",
        "transportadora",
        "shopee",
    ],
    "preco": [
        "preço",
        "preco",
        "barato",
        "caro",
        "desconto",
        "valor",
        "custo",
        "promoção",
        "promocao",
        "cupom",
        "double",
    ],
    "qualidade": [
        "qualidade",
        "produto",
        "defeito",
        "excelente",
        "ruim",
        "material",
        "acabamento",
        "original",
    ],
}

NEGATIVE_HINTS = [
    "não",
    "nao",
    "ruim",
    "péssim",
    "pessim",
    "atras",
    "decepc",
    "problema",
    "defeito",
    "danific",
]

POSITIVE_HINTS = [
    "ótimo",
    "otimo",
    "excelente",
    "adorei",
    "perfeito",
    "antes do prazo",
    "recomendo",
    "satisfeit",
    "bom",
]
