"""Repositório JSON com CRUD em memória e persistência em arquivo."""

import json
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.constants.dataset import (
    ANO_FIM,
    ANO_INICIO,
    DATASET_DESCRICAO,
    DATASET_NOME,
    DATASET_VERSION,
    FONTE_ANOTACAO,
    PLATAFORMA,
)
from app.models.aspecto import AspectoAnalise
from app.models.review import Review
from app.utils.csv_loader import load_reviews_from_csv, resolve_csv_path, resolve_json_path


class JsonReviewRepository:
    """Persiste avaliações em JSON; seed inicial a partir do CSV."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._reviews: list[Review] = []
        self._by_id: dict[str, Review] = {}
        self._loaded = False

    @property
    def json_path(self) -> Path:
        return resolve_json_path(self._settings.json_file_path)

    @property
    def csv_path(self) -> Path:
        return resolve_csv_path(self._settings.csv_file_path)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def _rebuild_index(self) -> None:
        self._by_id = {r.id: r for r in self._reviews if r.id}

    def _build_meta(self) -> dict[str, Any]:
        return {
            "version": DATASET_VERSION,
            "nome": DATASET_NOME,
            "descricao": DATASET_DESCRICAO,
            "plataforma": PLATAFORMA,
            "fonte_anotacao": FONTE_ANOTACAO,
            "ano_inicio": ANO_INICIO,
            "ano_fim": ANO_FIM,
            "periodo_campanha": "double_date",
        }

    def _save(self) -> None:
        path = self.json_path
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "meta": self._build_meta(),
            "avaliacoes": [r.to_dict() for r in self._reviews],
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _parse_stored_json(self, raw: Any) -> list[dict[str, Any]] | None:
        if isinstance(raw, dict):
            meta = raw.get("meta") or {}
            if meta.get("version") != DATASET_VERSION:
                return None
            avaliacoes = raw.get("avaliacoes")
            return avaliacoes if isinstance(avaliacoes, list) else None
        if isinstance(raw, list):
            return None
        return None

    def _load_from_json(self) -> bool:
        path = self.json_path
        if not path.exists():
            return False
        raw = json.loads(path.read_text(encoding="utf-8"))
        items = self._parse_stored_json(raw)
        if items is None:
            return False
        self._reviews = [Review.from_dict(item) for item in items]
        self._rebuild_index()
        self._loaded = True
        return True

    def _seed_from_csv(self) -> int:
        self._reviews = load_reviews_from_csv(self.csv_path, enrich=True)
        self._rebuild_index()
        self._save()
        self._loaded = True
        return len(self._reviews)

    def load(self, *, force_csv: bool = False) -> int:
        if force_csv or not self._load_from_json():
            if not self.csv_path.exists():
                raise FileNotFoundError(
                    f"Nem JSON ({self.json_path}) nem CSV ({self.csv_path}) encontrados."
                )
            return self._seed_from_csv()
        return len(self._reviews)

    def reload(self) -> int:
        self._loaded = False
        return self.load()

    def find_by_id(self, review_id: str) -> Review | None:
        return self._by_id.get(review_id)

    def _apply_filters(
        self,
        *,
        sentimento: str | None = None,
        periodo_promocional: str | None = None,
        search: str | None = None,
    ) -> list[Review]:
        result = self._reviews
        if sentimento:
            result = [r for r in result if r.sentimento == sentimento]
        if periodo_promocional:
            result = [
                r for r in result if r.periodo_promocional == periodo_promocional
            ]
        if search:
            term = search.lower()
            result = [r for r in result if term in r.texto.lower()]
        return result

    def find_all(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        sentimento: str | None = None,
        periodo_promocional: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Review], int]:
        filtered = self._apply_filters(
            sentimento=sentimento,
            periodo_promocional=periodo_promocional,
            search=search,
        )
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        return filtered[start:end], total

    def create(self, review: Review) -> Review:
        review.id = review.id or str(uuid.uuid4())
        self._reviews.append(review)
        self._by_id[review.id] = review
        self._save()
        return review

    def update(self, review_id: str, data: dict[str, Any]) -> Review | None:
        review = self.find_by_id(review_id)
        if not review:
            return None

        if "texto" in data and data["texto"] is not None:
            review.texto = data["texto"]
        if "sentimento" in data and data["sentimento"] is not None:
            review.sentimento = data["sentimento"]
        if "autor" in data and data["autor"] is not None:
            review.autor = data["autor"]
        if "periodo_promocional" in data and data["periodo_promocional"] is not None:
            review.periodo_promocional = data["periodo_promocional"]
        if "aspectos" in data and data["aspectos"] is not None:
            review.aspectos = [
                AspectoAnalise.from_dict(a) if isinstance(a, dict) else a
                for a in data["aspectos"]
            ]
        if "plataforma" in data and data["plataforma"] is not None:
            review.plataforma = data["plataforma"]
        if "fonte_anotacao" in data and data["fonte_anotacao"] is not None:
            review.fonte_anotacao = data["fonte_anotacao"]

        self._save()
        return review

    def delete(self, review_id: str) -> bool:
        review = self.find_by_id(review_id)
        if not review:
            return False
        self._reviews.remove(review)
        del self._by_id[review_id]
        self._save()
        return True

    def count(self, periodo_promocional: str | None = None) -> int:
        if not periodo_promocional:
            return len(self._reviews)
        return len(self._apply_filters(periodo_promocional=periodo_promocional))

    def stats_by_sentimento(
        self, periodo_promocional: str | None = None
    ) -> list[dict[str, Any]]:
        items = self._apply_filters(periodo_promocional=periodo_promocional)
        counter = Counter(r.sentimento for r in items)
        total = len(items) or 1
        return [
            {
                "sentimento": sentimento,
                "total": count,
                "percentual": round((count / total) * 100, 1),
            }
            for sentimento, count in counter.most_common()
        ]

    def stats_by_aspecto(
        self, periodo_promocional: str | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        from app.constants.promosense import ASPECTOS

        items = self._apply_filters(periodo_promocional=periodo_promocional)
        result: dict[str, list[dict[str, Any]]] = {}

        for aspecto_nome in ASPECTOS:
            counter: Counter[str] = Counter()
            for review in items:
                for asp in review.aspectos:
                    if asp.nome == aspecto_nome:
                        counter[asp.sentimento] += 1
                        break
            total = sum(counter.values()) or 1
            result[aspecto_nome] = [
                {
                    "sentimento": sentimento,
                    "total": count,
                    "percentual": round((count / total) * 100, 1),
                }
                for sentimento, count in counter.most_common()
            ]
        return result

    def list_periodos(self) -> list[dict[str, Any]]:
        from app.constants.promosense import PERIODOS_PROMOCIONAIS

        return [
            {
                "id": key,
                "label": meta["label"],
                "ano_inicio": meta["ano_inicio"],
                "ano_fim": meta["ano_fim"],
                "descricao": meta.get("descricao"),
            }
            for key, meta in PERIODOS_PROMOCIONAIS.items()
        ]

    def get_meta(self) -> dict[str, Any]:
        return self._build_meta()
