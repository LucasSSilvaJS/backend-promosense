"""Metadados do dataset Shopee Double Date."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_review_service
from app.schemas.review import DatasetInfoSchema
from app.security.rate_limit import limiter, read_limit
from app.services.review_service import ReviewService

router = APIRouter()


@router.get(
    "",
    response_model=DatasetInfoSchema,
    summary="Informações do dataset",
    description=(
        "Dataset de validação: avaliações reais Shopee (2024–2026), "
        "coletadas em Double Date, anotadas manualmente."
    ),
)
@limiter.limit(read_limit())
def get_dataset_info(
    request: Request,
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> DatasetInfoSchema:
    return service.get_dataset_info()
