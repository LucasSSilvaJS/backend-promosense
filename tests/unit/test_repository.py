"""Testes unitários — repositório JSON."""

import pytest

from app.models.aspecto import AspectoAnalise
from app.models.review import Review
from app.repositories.review_repository import JsonReviewRepository


@pytest.mark.unit
class TestJsonReviewRepository:
    @pytest.fixture
    def repository(self, test_env) -> JsonReviewRepository:
        repo = JsonReviewRepository()
        repo.load()
        return repo

    def test_load_seed_do_csv(self, repository) -> None:
        assert repository.is_loaded
        assert repository.count() == 5

    def test_find_by_id(self, repository) -> None:
        review = repository.find_by_id("0")
        assert review is not None
        assert review.sentimento == "positivo"

    def test_find_all_com_filtro_sentimento(self, repository) -> None:
        items, total = repository.find_all(sentimento="negativo", page_size=10)
        assert total == 2
        assert all(r.sentimento == "negativo" for r in items)

    def test_find_all_com_filtro_periodo(self, repository) -> None:
        items, total = repository.find_all(
            periodo_promocional="double_date", page_size=10
        )
        assert total == 5
        assert all(r.periodo_promocional == "double_date" for r in items)

    def test_create_update_delete(self, repository) -> None:
        review = Review(
            id=None,
            texto="nova avaliacao teste",
            sentimento="neutro",
            autor="Cliente Shopee #9999",
            plataforma="shopee",
            fonte_anotacao="validacao_manual",
            periodo_promocional="double_date",
            aspectos=[
                AspectoAnalise(nome="preco", sentimento="neutro"),
                AspectoAnalise(nome="entrega", sentimento="neutro"),
                AspectoAnalise(nome="qualidade", sentimento="neutro"),
            ],
        )
        created = repository.create(review)
        assert created.id is not None

        updated = repository.update(created.id, {"sentimento": "positivo"})
        assert updated is not None
        assert updated.sentimento == "positivo"

        assert repository.delete(created.id) is True
        assert repository.find_by_id(created.id) is None

    def test_stats_by_sentimento(self, repository) -> None:
        stats = repository.stats_by_sentimento()
        assert len(stats) >= 2
        assert all("sentimento" in s and "total" in s and "percentual" in s for s in stats)

    def test_list_periodos(self, repository) -> None:
        periodos = repository.list_periodos()
        ids = [p["id"] for p in periodos]
        assert ids == ["double_date"]
