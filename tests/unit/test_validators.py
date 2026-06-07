"""Testes unitários — validação de entrada."""

import pytest
from fastapi import HTTPException

from app.security.validators import sanitize_search


@pytest.mark.unit
class TestSanitizeSearch:
    def test_none_retorna_none(self) -> None:
        assert sanitize_search(None) is None

    def test_texto_valido(self) -> None:
        assert sanitize_search("  entrega rapida  ") == "entrega rapida"

    def test_texto_vazio_retorna_none(self) -> None:
        assert sanitize_search("   ") is None

    def test_texto_longo_rejeitado(self) -> None:
        with pytest.raises(HTTPException) as exc:
            sanitize_search("a" * 201)
        assert exc.value.status_code == 422

    def test_caractere_controle_rejeitado(self) -> None:
        with pytest.raises(HTTPException) as exc:
            sanitize_search("texto\x00invalido")
        assert exc.value.status_code == 422
