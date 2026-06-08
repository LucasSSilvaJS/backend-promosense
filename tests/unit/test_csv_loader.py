"""Testes unitários — parse CSV."""

import pytest

from app.models.review import Review
from app.utils.csv_loader import load_reviews_from_csv, parse_csv_row


@pytest.mark.unit
class TestParseCsvRow:
    def test_linha_valida(self) -> None:
        row = {"texto": "  otimo produto  ", "sentimento": "Positivo", "aspecto": "", "sentimento_aspecto": ""}
        review = parse_csv_row(row)
        assert review is not None
        assert review.texto == "otimo produto"
        assert review.sentimento == "positivo"

    def test_linha_sem_texto_retorna_none(self) -> None:
        row = {"texto": "", "sentimento": "positivo", "aspecto": "", "sentimento_aspecto": ""}
        assert parse_csv_row(row) is None

    def test_sentimento_invalido_retorna_none(self) -> None:
        row = {"texto": "texto", "sentimento": "feliz", "aspecto": "", "sentimento_aspecto": ""}
        assert parse_csv_row(row) is None


@pytest.mark.unit
class TestLoadReviewsFromCsv:
    def test_carrega_fixture_enriquecida(self, sample_csv_path) -> None:
        reviews = load_reviews_from_csv(sample_csv_path, enrich=True)
        assert len(reviews) == 5
        assert all(isinstance(r, Review) for r in reviews)
        assert reviews[0].plataforma == "shopee"
        assert reviews[0].fonte_anotacao == "validacao_manual"
        assert reviews[0].periodo_promocional == "double_date"
        assert len(reviews[0].aspectos) == 3

    def test_arquivo_inexistente_levanta_erro(self, tmp_path) -> None:
        with pytest.raises(FileNotFoundError):
            load_reviews_from_csv(tmp_path / "inexistente.csv")
