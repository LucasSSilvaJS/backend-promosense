"""Endpoints de saúde da aplicação."""

from fastapi import APIRouter, Request

from app.api.deps import get_review_repository
from app.config import get_settings
from app.constants.dataset import ANO_FIM, ANO_INICIO, PLATAFORMA
from app.security.rate_limit import limiter

router = APIRouter()
_read_limit = f"{get_settings().rate_limit_per_minute}/minute"


@router.get(
    "/health",
    summary="Verificar saúde da API",
    description="Status da API e do dataset Shopee Double Date (2024–2026).",
)
@limiter.limit(_read_limit)
def health_check(request: Request) -> dict:
    repository = get_review_repository()
    meta = repository.get_meta() if repository.is_loaded else {}
    return {
        "status": "ok" if repository.is_loaded else "degraded",
        "api": "online",
        "dataset": {
            "plataforma": PLATAFORMA,
            "periodo": "double_date",
            "anos": f"{ANO_INICIO}-{ANO_FIM}",
            "fonte_anotacao": meta.get("fonte_anotacao", "validacao_manual"),
            "version": meta.get("version"),
        },
        "records_loaded": repository.count() if repository.is_loaded else 0,
    }
