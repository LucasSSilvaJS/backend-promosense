"""Configurações da aplicação carregadas via variáveis de ambiente."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants.dataset import DATASET_DESCRICAO


class Settings(BaseSettings):
    """Configurações centralizadas lidas do arquivo .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "PromoSense API"
    api_version: str = "1.0.0"
    api_description: str = DATASET_DESCRICAO

    csv_file_path: str = "olist_processado.csv"
    json_file_path: str = "data/avaliacoes.json"

    # Segurança
    environment: str = "development"
    auth_enabled: bool = True
    api_key: str = ""
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 120
    cors_origins: str = (
        "http://localhost:3000,http://localhost:5173,https://promosense.vercel.app"
    )
    allowed_hosts: str = "*"
    docs_enabled: bool = True

    @field_validator("rate_limit_per_minute")
    @classmethod
    def validate_rate_limit(cls, value: int) -> int:
        return max(10, min(value, 10_000))

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.cors_origins.strip():
            return []
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_hosts_list(self) -> list[str]:
        if self.allowed_hosts.strip() in ("", "*"):
            return ["*"]
        return [h.strip() for h in self.allowed_hosts.split(",") if h.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Retorna instância única (singleton) das configurações."""
    return Settings()
