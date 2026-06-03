"""Ponto de entrada da aplicação FastAPI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.deps import get_review_repository
from app.api.v1.router import api_router
from app.config import get_settings
from app.constants.dataset import DATASET_NOME
from app.security.middleware import SecurityHeadersMiddleware
from app.security.rate_limit import limiter


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Carrega dataset Shopee Double Date (JSON ou seed do CSV anotado)."""
    settings = get_settings()
    if settings.auth_enabled and not settings.api_key:
        print("AVISO: AUTH_ENABLED=true mas API_KEY não definida — escritas bloqueadas.")

    repository = get_review_repository()
    try:
        count = repository.load()
        print(f"{DATASET_NOME}: {count} avaliações ({repository.json_path})")
    except FileNotFoundError as exc:
        print(f"Aviso: {exc}")
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    docs_url = "/docs" if settings.docs_enabled else None
    redoc_url = "/redoc" if settings.docs_enabled else None
    openapi_url = "/openapi.json" if settings.docs_enabled else None

    application = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    if settings.rate_limit_enabled:
        limiter._default_limits = [f"{settings.rate_limit_per_minute}/minute"]
        application.add_middleware(SlowAPIMiddleware)

    if settings.allowed_hosts_list != ["*"]:
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts_list,
        )

    application.add_middleware(
        SecurityHeadersMiddleware,
        enable_hsts=settings.is_production,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list or ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-API-Key", "Authorization"],
    )

    application.include_router(api_router)

    def custom_openapi():
        if application.openapi_schema:
            return application.openapi_schema
        schema = get_openapi(
            title=application.title,
            version=application.version,
            description=application.description,
            routes=application.routes,
        )
        schema["components"]["securitySchemes"] = {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "Obrigatória para POST, PUT e DELETE quando AUTH_ENABLED=true.",
            }
        }
        application.openapi_schema = schema
        return application.openapi_schema

    application.openapi = custom_openapi

    @application.get("/", tags=["Root"], include_in_schema=False)
    def root() -> dict:
        return {
            "message": "PromoSense API — Shopee Double Date (2024–2026)",
            "docs": "/docs" if settings.docs_enabled else None,
            "dataset": "/api/v1/dataset",
            "avaliacoes": "/api/v1/avaliacoes",
            "dashboard": "/api/v1/dashboard",
        }

    return application


app = create_app()
