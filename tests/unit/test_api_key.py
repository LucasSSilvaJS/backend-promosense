"""Testes unitários — autenticação API Key."""

import pytest
from fastapi import HTTPException

from app.security.api_key import _is_valid_key, require_api_key


@pytest.mark.unit
class TestApiKey:
    def test_chave_valida(self) -> None:
        assert _is_valid_key("abc123", "abc123") is True

    def test_chave_invalida(self) -> None:
        assert _is_valid_key("errada", "correta") is False

    def test_chave_vazia(self) -> None:
        assert _is_valid_key(None, "correta") is False

    def test_require_api_key_rejeita_sem_header(self, test_env, monkeypatch) -> None:
        from app.config import get_settings

        settings = get_settings()
        with pytest.raises(HTTPException) as exc:
            require_api_key(api_key=None, settings=settings)
        assert exc.value.status_code == 401

    def test_require_api_key_aceita_chave_correta(self, test_env) -> None:
        from app.config import get_settings

        settings = get_settings()
        require_api_key(api_key="test-api-key-segura", settings=settings)

    def test_auth_desabilitado_nao_exige_chave(self, test_env, monkeypatch) -> None:
        from app.config import Settings, get_settings

        get_settings.cache_clear()
        monkeypatch.setenv("AUTH_ENABLED", "false")
        get_settings.cache_clear()

        settings = Settings()
        require_api_key(api_key=None, settings=settings)
