"""CRUD de avaliações — formato PromoSense (/avaliacoes)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import get_review_service
from app.schemas.review import (
    AvaliacaoCreateSchema,
    AvaliacaoListSchema,
    AvaliacaoSchema,
    AvaliacaoUpdateSchema,
    PeriodoListSchema,
)
from app.security.api_key import require_api_key
from app.security.rate_limit import limiter, read_limit, write_limit
from app.security.validators import sanitize_search
from app.services.review_service import ReviewService

router = APIRouter()


@router.get(
    "/periodos",
    response_model=PeriodoListSchema,
    summary="Listar períodos promocionais",
    description="Edições Double Date Shopee (2024, 2025, 2026).",
)
@limiter.limit(read_limit())
def list_periodos(
    request: Request,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> PeriodoListSchema:
    return service.list_periodos()


@router.get(
    "",
    response_model=AvaliacaoListSchema,
    summary="Listar avaliações (JSON)",
    description="Lista paginada com filtro por período promocional e sentimento.",
)
@limiter.limit(read_limit())
def list_avaliacoes(
    request: Request,
    service: Annotated[ReviewService, Depends(get_review_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=500, description="Padrão 10 como no front."),
    sentimento: str | None = Query(None),
    periodo_promocional: str | None = Query(
        None,
        description="double_date_2024 | double_date_2025 | double_date_2026",
    ),
    search: str | None = Query(None, description="Busca no texto da avaliação."),
) -> AvaliacaoListSchema:
    return service.list_reviews(
        page=page,
        page_size=page_size,
        sentimento=sentimento,
        periodo_promocional=periodo_promocional,
        search=sanitize_search(search),
    )


@router.get(
    "/{avaliacao_id}",
    response_model=AvaliacaoSchema,
    summary="Buscar avaliação por ID",
)
@limiter.limit(read_limit())
def get_avaliacao(
    request: Request,
    avaliacao_id: str,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> AvaliacaoSchema:
    avaliacao = service.get_by_id(avaliacao_id)
    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada.",
        )
    return avaliacao


@router.post(
    "",
    response_model=AvaliacaoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Criar avaliação",
    dependencies=[Depends(require_api_key)],
)
@limiter.limit(write_limit())
def create_avaliacao(
    request: Request,
    payload: AvaliacaoCreateSchema,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> AvaliacaoSchema:
    return service.create(payload)


@router.put(
    "/{avaliacao_id}",
    response_model=AvaliacaoSchema,
    summary="Atualizar avaliação",
    dependencies=[Depends(require_api_key)],
)
@limiter.limit(write_limit())
def update_avaliacao(
    request: Request,
    avaliacao_id: str,
    payload: AvaliacaoUpdateSchema,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> AvaliacaoSchema:
    avaliacao = service.update(avaliacao_id, payload)
    if not avaliacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada.",
        )
    return avaliacao


@router.delete(
    "/{avaliacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover avaliação",
    dependencies=[Depends(require_api_key)],
)
@limiter.limit(write_limit())
def delete_avaliacao(
    request: Request,
    avaliacao_id: str,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> None:
    if not service.delete(avaliacao_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada.",
        )
