"""Autenticação por API Key para operações sensíveis."""

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import Settings, get_settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def _is_valid_key(provided: str | None, expected: str) -> bool:
    if not provided or not expected:
        return False
    return secrets.compare_digest(provided.strip(), expected.strip())


def require_api_key(
    api_key: Annotated[str | None, Security(API_KEY_HEADER)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """
    Exige API Key válida quando AUTH_ENABLED=true.
    Usado em POST, PUT e DELETE.
    """
    if not settings.auth_enabled:
        return

    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Autenticação não configurada no servidor.",
        )

    if not _is_valid_key(api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou ausente.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
