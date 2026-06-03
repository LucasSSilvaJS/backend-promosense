"""Rotas legadas /reviews (alias para /avaliacoes)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import get_review_service
from app.schemas.review import (
    AvaliacaoCreateSchema,
    AvaliacaoUpdateSchema,
    ReviewListSchema,
    ReviewSchema,
    ReviewStatsSchema,
)
from app.security.api_key import require_api_key
from app.security.rate_limit import limiter, read_limit, write_limit
from app.security.validators import sanitize_search
from app.services.review_service import ReviewService

router = APIRouter()


@router.get("", response_model=ReviewListSchema, summary="Listar reviews (legado)")
@limiter.limit(read_limit())
def list_reviews(
    request: Request,
    service: Annotated[ReviewService, Depends(get_review_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    sentimento: str | None = Query(None),
    periodo_promocional: str | None = Query(None),
    search: str | None = Query(None),
) -> ReviewListSchema:
    return service.list_reviews_legacy(
        page=page,
        page_size=page_size,
        sentimento=sentimento,
        periodo_promocional=periodo_promocional,
        search=sanitize_search(search),
    )


@router.get("/stats", response_model=ReviewStatsSchema, summary="Estatísticas (legado)")
@limiter.limit(read_limit())
def get_stats(
    request: Request,
    service: Annotated[ReviewService, Depends(get_review_service)],
    periodo_promocional: str | None = Query(None),
) -> ReviewStatsSchema:
    return service.get_stats(periodo_promocional)


@router.get("/{review_id}", response_model=ReviewSchema, summary="Buscar por ID (legado)")
@limiter.limit(read_limit())
def get_review(
    request: Request,
    review_id: str,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewSchema:
    review = service.get_by_id_legacy(review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não encontrado.")
    return review


@router.post(
    "",
    response_model=ReviewSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
@limiter.limit(write_limit())
def create_review(
    request: Request,
    payload: AvaliacaoCreateSchema,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewSchema:
    created = service.create(payload)
    return ReviewSchema(**created.model_dump())


@router.put(
    "/{review_id}",
    response_model=ReviewSchema,
    dependencies=[Depends(require_api_key)],
)
@limiter.limit(write_limit())
def update_review(
    request: Request,
    review_id: str,
    payload: AvaliacaoUpdateSchema,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewSchema:
    updated = service.update(review_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não encontrado.")
    return ReviewSchema(**updated.model_dump())


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key)],
)
@limiter.limit(write_limit())
def delete_review(
    request: Request,
    review_id: str,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> None:
    if not service.delete(review_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não encontrado.")
