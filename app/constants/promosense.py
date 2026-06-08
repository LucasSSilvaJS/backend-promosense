"""Período Double Date (Shopee) e aspectos de análise."""

from app.constants.dataset import ANO_FIM, ANO_INICIO

PERIODO_DOUBLE_DATE = "double_date"

# Coleta agregada 2024–2026 — o CSV não distingue data por registro
PERIODOS_PROMOCIONAIS: dict[str, dict] = {
    PERIODO_DOUBLE_DATE: {
        "label": f"Double Date ({ANO_INICIO}–{ANO_FIM})",
        "ano_inicio": ANO_INICIO,
        "ano_fim": ANO_FIM,
        "descricao": (
            f"Avaliações coletadas na Shopee entre {ANO_INICIO} e {ANO_FIM} "
            "durante campanhas Double Date. O CSV não contém data por registro."
        ),
    }
}

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
