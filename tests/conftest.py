"""Fixtures compartilhadas para testes."""

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CSV = FIXTURES_DIR / "sample.csv"
TEST_API_KEY = "test-api-key-segura"


@pytest.fixture
def sample_csv_path() -> Path:
    return SAMPLE_CSV


@pytest.fixture
def test_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Configura ambiente isolado com CSV de fixture e JSON temporário."""
    json_path = tmp_path / "avaliacoes.json"

    monkeypatch.setenv("CSV_FILE_PATH", str(SAMPLE_CSV))
    monkeypatch.setenv("JSON_FILE_PATH", str(json_path))
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("API_KEY", TEST_API_KEY)
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("ALLOWED_HOSTS", "*")
    monkeypatch.setenv("DOCS_ENABLED", "true")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")

    _clear_caches()
    yield tmp_path
    _clear_caches()


@pytest.fixture
def client(test_env: Path) -> Generator[TestClient, None, None]:
    """Cliente HTTP para testes de integração/sistema."""
    from app.main import create_app

    app = create_app()
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-API-Key": TEST_API_KEY}


def _clear_caches() -> None:
    from app.api.deps import get_review_repository
    from app.config import get_settings

    get_settings.cache_clear()
    get_review_repository.cache_clear()
