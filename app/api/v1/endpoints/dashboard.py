"""Dashboard analítico PromoSense."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_review_service
from app.config import get_settings
from app.schemas.review import DashboardSchema, ReviewStatsSchema
from app.security.rate_limit import limiter
from app.services.review_service import ReviewService

router = APIRouter()
_read_limit = f"{get_settings().rate_limit_per_minute}/minute"


@router.get(
    "",
    response_model=DashboardSchema,
    summary="Dashboard de sentimento",
    description=(
        "Distribuição geral e por aspecto (preço, entrega, qualidade). "
        "Use periodo_promocional para filtrar como no front."
    ),
)
@limiter.limit(_read_limit)
def get_dashboard(
    request: Request,
    service: Annotated[ReviewService, Depends(get_review_service)],
    periodo_promocional: str | None = Query(
        None,
        description="Filtro: double_date_2024 | double_date_2025 | double_date_2026",
    ),
) -> DashboardSchema:
    return service.get_dashboard(periodo_promocional)


@router.get(
    "/resumo",
    response_model=ReviewStatsSchema,
    summary="Resumo de contagens por sentimento",
)
@limiter.limit(_read_limit)
def get_resumo(
    request: Request,
    service: Annotated[ReviewService, Depends(get_review_service)],
    periodo_promocional: str | None = Query(None),
) -> ReviewStatsSchema:
    return service.get_stats(periodo_promocional)
