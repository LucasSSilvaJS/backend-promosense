"""Roteador principal da API v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import avaliacoes, dashboard, dataset, health, reviews

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(
    dataset.router,
    prefix="/dataset",
    tags=["Dataset — Shopee Double Date"],
)
api_router.include_router(
    avaliacoes.router,
    prefix="/avaliacoes",
    tags=["Avaliações — Shopee Double Date"],
)
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard — PromoSense"],
)
api_router.include_router(
    reviews.router,
    prefix="/reviews",
    tags=["Reviews (legado)"],
)
