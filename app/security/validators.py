"""Validação e sanitização de entradas."""

from fastapi import HTTPException, status

_MAX_SEARCH_LENGTH = 200


def sanitize_search(value: str | None) -> str | None:
    """Limita tamanho e bloqueia caracteres de controle na busca."""
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if len(cleaned) > _MAX_SEARCH_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Busca excede {_MAX_SEARCH_LENGTH} caracteres.",
        )
    if any(ord(char) < 32 for char in cleaned):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Busca contém caracteres inválidos.",
        )
    return cleaned
