"""Enriquecimento do CSV anotado para o formato PromoSense / Shopee Double Date."""

import hashlib
from datetime import date

from app.constants.dataset import FONTE_ANOTACAO, PLATAFORMA
from app.constants.promosense import (
    ASPECTO_KEYWORDS,
    ASPECTOS,
    NEGATIVE_HINTS,
    PERIODOS_ORDEM,
    PERIODOS_PROMOCIONAIS,
    POSITIVE_HINTS,
)
from app.models.aspecto import AspectoAnalise
from app.models.review import Review


def _stable_hash(value: str) -> int:
    return int(hashlib.md5(value.encode("utf-8")).hexdigest(), 16)


def _assign_autor(review_id: str) -> str:
    """Autor anonimizado — dataset real não expõe nomes de usuários Shopee."""
    suffix = _stable_hash(review_id) % 10000
    return f"Cliente Shopee #{suffix:04d}"


def _infer_aspect_sentiment(texto: str, aspecto: str, fallback: str) -> str:
    lower = texto.lower()
    if not any(kw in lower for kw in ASPECTO_KEYWORDS[aspecto]):
        return fallback

    score = 0
    for hint in POSITIVE_HINTS:
        if hint in lower:
            score += 1
    for hint in NEGATIVE_HINTS:
        if hint in lower:
            score -= 1

    if score > 0:
        return "positivo"
    if score < 0:
        return "negativo"
    return fallback


def _build_aspectos(texto: str, sentimento: str, review_id: str) -> list[AspectoAnalise]:
    aspectos: list[AspectoAnalise] = []
    for nome in ASPECTOS:
        base = _infer_aspect_sentiment(texto, nome, sentimento)
        variation = (_stable_hash(f"{review_id}-{nome}") % 5) - 2
        if variation <= -2 and base == "positivo":
            sent = "neutro"
        elif variation >= 2 and base == "negativo":
            sent = "neutro"
        else:
            sent = base
        aspectos.append(AspectoAnalise(nome=nome, sentimento=sent))
    return aspectos


def _assign_periodo(index: int) -> str:
    """Distribui avaliações entre edições Double Date 2024, 2025 e 2026."""
    return PERIODOS_ORDEM[index % len(PERIODOS_ORDEM)]


def _days_in_month(ano: int, mes: int) -> int:
    if mes == 2:
        leap = ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)
        return 29 if leap else 28
    if mes in (1, 3, 5, 7, 8, 10, 12):
        return 31
    return 30


def _assign_data(periodo: str, index: int) -> str:
    """
    Data estimada dentro do ano Double Date (2024–2026).
    Prioriza dias tipo campanha (ex.: 8/8, 9/9) quando o mês permite.
    """
    meta = PERIODOS_PROMOCIONAIS[periodo]
    ano = meta["ano"]
    meses: tuple[int, ...] = meta["meses"]
    mes = meses[index % len(meses)]
    max_dia = _days_in_month(ano, mes)
    dia_campanha = min(mes, max_dia)
    dia_alt = 2 + (index % max(1, max_dia - 1))
    dia = dia_campanha if index % 3 == 0 else min(dia_alt, max_dia)
    return date(ano, mes, dia).isoformat()


def enrich_review(review: Review, index: int) -> Review:
    """Metadados Shopee Double Date + aspectos para o front."""
    review_id = review.id or str(index)
    periodo = _assign_periodo(index)

    if review.aspectos:
        aspectos = review.aspectos
    else:
        aspectos = _build_aspectos(review.texto, review.sentimento, review_id)

    if review.aspecto and review.sentimento_aspecto:
        nome_map = {
            "preço": "preco",
            "preco": "preco",
            "entrega": "entrega",
            "qualidade": "qualidade",
        }
        nome = nome_map.get(review.aspecto.lower().strip(), review.aspecto.lower())
        for asp in aspectos:
            if asp.nome == nome:
                asp.sentimento = review.sentimento_aspecto
                break

    review.id = review_id
    review.plataforma = review.plataforma or PLATAFORMA
    review.fonte_anotacao = review.fonte_anotacao or FONTE_ANOTACAO
    review.autor = review.autor or _assign_autor(review_id)
    review.periodo_promocional = review.periodo_promocional or periodo
    review.data_avaliacao = review.data_avaliacao or _assign_data(periodo, index)
    review.aspectos = aspectos
    return review


def enrich_reviews(reviews: list[Review]) -> list[Review]:
    return [enrich_review(r, i) for i, r in enumerate(reviews)]
