"""Rate limiting com SlowAPI (somente em rotas decoradas)."""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def read_limit() -> str:
    from app.config import get_settings

    if not get_settings().rate_limit_enabled:
        return "10000/minute"
    return f"{get_settings().rate_limit_per_minute}/minute"


def write_limit() -> str:
    from app.config import get_settings

    if not get_settings().rate_limit_enabled:
        return "10000/minute"
    return "30/minute"
