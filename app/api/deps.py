"""Dependências injetáveis do FastAPI."""

from functools import lru_cache

from app.repositories.review_repository import JsonReviewRepository
from app.services.review_service import ReviewService


@lru_cache
def get_review_repository() -> JsonReviewRepository:
    repository = JsonReviewRepository()
    if not repository.is_loaded:
        repository.load()
    return repository


def get_review_service() -> ReviewService:
    return ReviewService(get_review_repository())
