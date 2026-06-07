"""Testes unitários — serviço de avaliações."""

import pytest

from app.repositories.review_repository import JsonReviewRepository
from app.schemas.review import AvaliacaoCreateSchema
from app.services.review_service import ReviewService


@pytest.mark.unit
class TestReviewService:
    @pytest.fixture
    def service(self, test_env) -> ReviewService:
        repo = JsonReviewRepository()
        repo.load()
        return ReviewService(repo)

    def test_list_reviews_paginado(self, service) -> None:
        result = service.list_reviews(page=1, page_size=2)
        assert result.total == 5
        assert len(result.items) == 2
        assert result.items[0].plataforma == "shopee"

    def test_get_by_id(self, service) -> None:
        item = service.get_by_id("0")
        assert item is not None
        assert item.id == "0"

    def test_get_dashboard(self, service) -> None:
        dash = service.get_dashboard()
        assert dash.total_avaliacoes == 5
        assert len(dash.distribuicao_sentimento) >= 2
        assert len(dash.sentimento_por_aspecto) == 3

    def test_get_dataset_info(self, service) -> None:
        info = service.get_dataset_info()
        assert info.plataforma == "shopee"
        assert info.total_avaliacoes == 5

    def test_create_avaliacao(self, service) -> None:
        payload = AvaliacaoCreateSchema(
            texto="servico unitario teste",
            sentimento="positivo",
            autor="Cliente Shopee #0001",
            periodo_promocional="double_date_2024",
            data_avaliacao="2024-03-03",
            aspectos=[],
        )
        created = service.create(payload)
        assert created.texto == "servico unitario teste"
        assert len(created.aspectos) == 3
