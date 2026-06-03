"""Leitura e parse do arquivo CSV de reviews."""

import csv
from pathlib import Path

from app.models.review import Review
from app.utils.enrichment import enrich_reviews

VALID_SENTIMENTOS = {"positivo", "negativo", "neutro"}


def _normalize_sentimento(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    normalized = value.strip().lower()
    return normalized if normalized in VALID_SENTIMENTOS else None


def parse_csv_row(row: dict[str, str]) -> Review | None:
    """Converte uma linha do CSV em Review, ou None se inválida."""
    texto = (row.get("texto") or "").strip()
    sentimento = _normalize_sentimento(row.get("sentimento"))
    if not texto or not sentimento:
        return None

    aspecto = (row.get("aspecto") or "").strip() or None
    sentimento_aspecto = _normalize_sentimento(row.get("sentimento_aspecto"))

    return Review(
        texto=texto,
        sentimento=sentimento,
        aspecto=aspecto,
        sentimento_aspecto=sentimento_aspecto,
    )


def resolve_csv_path(csv_path: str | Path) -> Path:
    """Resolve caminho absoluto do arquivo CSV."""
    path = Path(csv_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def resolve_json_path(json_path: str | Path) -> Path:
    path = Path(json_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def load_reviews_from_csv(csv_path: str | Path, *, enrich: bool = True) -> list[Review]:
    """Carrega reviews válidos do CSV; opcionalmente enriquece para PromoSense."""
    path = resolve_csv_path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {path}")

    reviews: list[Review] = []
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader):
            review = parse_csv_row(row)
            if review is None:
                continue
            review.id = str(len(reviews))
            reviews.append(review)

    if enrich:
        reviews = enrich_reviews(reviews)
    return reviews
