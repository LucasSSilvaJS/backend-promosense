"""Testes unitários — enriquecimento Shopee Double Date."""

import pytest

from app.models.review import Review
from app.utils.enrichment import enrich_review


@pytest.mark.unit
class TestEnrichment:
    def test_adiciona_metadados_shopee(self) -> None:
        review = Review(texto="entrega rapida", sentimento="positivo")
        enriched = enrich_review(review, index=0)

        assert enriched.plataforma == "shopee"
        assert enriched.fonte_anotacao == "validacao_manual"
        assert enriched.autor.startswith("Cliente Shopee #")
        assert enriched.periodo_promocional == "double_date"
        assert len(enriched.aspectos) == 3

    def test_periodo_unico_independente_do_indice(self) -> None:
        r0 = enrich_review(Review(texto="a", sentimento="positivo"), 0)
        r1 = enrich_review(Review(texto="b", sentimento="positivo"), 1)
        r2 = enrich_review(Review(texto="c", sentimento="positivo"), 2)

        assert r0.periodo_promocional == "double_date"
        assert r1.periodo_promocional == "double_date"
        assert r2.periodo_promocional == "double_date"
