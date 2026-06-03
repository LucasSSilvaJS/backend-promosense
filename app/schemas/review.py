"""Schemas Pydantic — Shopee Double Date (validação manual 2024–2026)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.constants.dataset import (
    ANO_FIM,
    ANO_INICIO,
    DATASET_DESCRICAO,
    DATASET_NOME,
    FONTE_ANOTACAO,
    PLATAFORMA,
)
from app.constants.promosense import ASPECTO_LABELS, PERIODOS_PROMOCIONAIS

SentimentoLiteral = Literal["positivo", "negativo", "neutro"]
PeriodoLiteral = Literal[
    "double_date_2024",
    "double_date_2025",
    "double_date_2026",
]
AspectoNomeLiteral = Literal["preco", "entrega", "qualidade"]


class AspectoSchema(BaseModel):
    """Análise de sentimento por aspecto (Preço, Entrega, Qualidade)."""

    nome: AspectoNomeLiteral = Field(..., description="Identificador do aspecto.")
    label: str = Field(..., description="Rótulo exibido no front.")
    sentimento: SentimentoLiteral


class AspectoInputSchema(BaseModel):
    nome: AspectoNomeLiteral
    sentimento: SentimentoLiteral


class AvaliacaoBaseSchema(BaseModel):
    texto: str = Field(..., min_length=1, description="Texto da avaliação Shopee.")
    sentimento: SentimentoLiteral = Field(
        ..., description="Sentimento geral anotado manualmente."
    )
    autor: str = Field(..., min_length=1, description="Identificador anonimizado do cliente.")
    plataforma: str = Field(default=PLATAFORMA, description="Marketplace de origem.")
    fonte_anotacao: str = Field(
        default=FONTE_ANOTACAO,
        description="Tipo de dataset (validação manual).",
    )
    periodo_promocional: PeriodoLiteral = Field(
        ..., description="Edição Double Date (2024, 2025 ou 2026)."
    )
    data_avaliacao: str = Field(
        ...,
        description="Data da avaliação no período Double Date (YYYY-MM-DD).",
    )
    aspectos: list[AspectoInputSchema] = Field(
        default_factory=list,
        description="Sentimento por aspecto: preço, entrega, qualidade.",
    )


class AvaliacaoCreateSchema(AvaliacaoBaseSchema):
    """Payload para criar avaliação."""


class AvaliacaoUpdateSchema(BaseModel):
    texto: str | None = Field(None, min_length=1)
    sentimento: SentimentoLiteral | None = None
    autor: str | None = None
    plataforma: str | None = None
    fonte_anotacao: str | None = None
    periodo_promocional: PeriodoLiteral | None = None
    data_avaliacao: str | None = None
    aspectos: list[AspectoInputSchema] | None = None


class AvaliacaoSchema(AvaliacaoBaseSchema):
    """Avaliação retornada pela API (formato PromoSense)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    periodo_label: str = Field(..., description="Nome exibido do período promocional.")
    aspectos: list[AspectoSchema]


class AvaliacaoListSchema(BaseModel):
    total: int
    page: int
    page_size: int
    periodo_promocional: str | None = None
    items: list[AvaliacaoSchema]


class SentimentoCountSchema(BaseModel):
    sentimento: str
    total: int
    percentual: float


class AspectoStatsGroupSchema(BaseModel):
    aspecto: str
    label: str
    distribuicao: list[SentimentoCountSchema]


class DashboardSchema(BaseModel):
    """Payload do dashboard PromoSense."""

    total_avaliacoes: int
    periodo_promocional: str | None = None
    periodo_label: str | None = None
    distribuicao_sentimento: list[SentimentoCountSchema]
    sentimento_por_aspecto: list[AspectoStatsGroupSchema]


class PeriodoSchema(BaseModel):
    id: str
    label: str
    ano: int
    descricao: str | None = None


class PeriodoListSchema(BaseModel):
    items: list[PeriodoSchema]


class DatasetInfoSchema(BaseModel):
    """Metadados do dataset de validação."""

    nome: str
    descricao: str
    plataforma: str
    fonte_anotacao: str
    ano_inicio: int
    ano_fim: int
    periodos: list[PeriodoSchema]
    total_avaliacoes: int = 0


# Aliases legados (/reviews)
class ReviewSchema(AvaliacaoSchema):
    pass


class ReviewListSchema(AvaliacaoListSchema):
    pass


class ReviewStatsSchema(BaseModel):
    total_reviews: int
    por_sentimento: list[SentimentoCountSchema]


def periodo_label(periodo_id: str | None) -> str:
    if not periodo_id:
        return "Todos os Double Dates (2024–2026)"
    meta = PERIODOS_PROMOCIONAIS.get(periodo_id)
    return meta["label"] if meta else periodo_id


def dataset_info(total: int = 0) -> DatasetInfoSchema:
    return DatasetInfoSchema(
        nome=DATASET_NOME,
        descricao=DATASET_DESCRICAO,
        plataforma=PLATAFORMA,
        fonte_anotacao=FONTE_ANOTACAO,
        ano_inicio=ANO_INICIO,
        ano_fim=ANO_FIM,
        periodos=[
            PeriodoSchema(
                id=key,
                label=meta["label"],
                ano=meta["ano"],
                descricao=meta.get("descricao"),
            )
            for key, meta in PERIODOS_PROMOCIONAIS.items()
        ],
        total_avaliacoes=total,
    )


def build_aspecto_schemas(aspectos: list) -> list[AspectoSchema]:
    built: list[AspectoSchema] = []
    for asp in aspectos:
        nome = asp.nome if hasattr(asp, "nome") else asp["nome"]
        sentimento = asp.sentimento if hasattr(asp, "sentimento") else asp["sentimento"]
        built.append(
            AspectoSchema(
                nome=nome,
                label=ASPECTO_LABELS.get(nome, nome),
                sentimento=sentimento,
            )
        )
    return built
