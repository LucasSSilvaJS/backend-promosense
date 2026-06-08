"""Metadados do dataset de validação Shopee / Double Date."""

DATASET_NOME = "Dataset de validação — Shopee Double Date"
DATASET_DESCRICAO = (
    "Avaliações reais coletadas na Shopee entre 2024 e 2026, "
    "durante períodos promocionais Double Date, com sentimento anotado manualmente. "
    "O CSV não distingue data por registro."
)

PLATAFORMA = "shopee"
FONTE_ANOTACAO = "validacao_manual"
ANO_INICIO = 2024
ANO_FIM = 2026

# Versão do schema de persistência; altere para forçar reimportação do CSV
DATASET_VERSION = "3"
