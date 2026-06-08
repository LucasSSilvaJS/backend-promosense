"""Testes de integração — endpoints HTTP."""

import pytest


@pytest.mark.integration
class TestHealthEndpoint:
    def test_health_retorna_ok(self, client) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["api"] == "online"
        assert data["dataset"]["plataforma"] == "shopee"
        assert data["records_loaded"] == 5


@pytest.mark.integration
class TestRootEndpoint:
    def test_root_retorna_links(self, client) -> None:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "avaliacoes" in data
        assert "dashboard" in data

    def test_docs_disponivel(self, client) -> None:
        response = client.get("/docs")
        assert response.status_code == 200


@pytest.mark.integration
class TestDatasetEndpoint:
    def test_dataset_metadados(self, client) -> None:
        response = client.get("/api/v1/dataset")
        assert response.status_code == 200
        data = response.json()
        assert data["plataforma"] == "shopee"
        assert data["fonte_anotacao"] == "validacao_manual"
        assert data["total_avaliacoes"] == 5
        assert len(data["periodos"]) == 1
        assert data["periodos"][0]["id"] == "double_date"


@pytest.mark.integration
class TestAvaliacoesEndpoints:
    def test_listar_periodos(self, client) -> None:
        response = client.get("/api/v1/avaliacoes/periodos")
        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["id"] == "double_date"

    def test_listar_avaliacoes_paginado(self, client) -> None:
        response = client.get("/api/v1/avaliacoes?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert "aspectos" in data["items"][0]

    def test_filtrar_por_sentimento(self, client) -> None:
        response = client.get("/api/v1/avaliacoes?sentimento=negativo")
        assert response.status_code == 200
        items = response.json()["items"]
        assert all(i["sentimento"] == "negativo" for i in items)

    def test_buscar_por_id(self, client) -> None:
        response = client.get("/api/v1/avaliacoes/0")
        assert response.status_code == 200
        assert response.json()["id"] == "0"

    def test_id_inexistente_retorna_404(self, client) -> None:
        response = client.get("/api/v1/avaliacoes/99999")
        assert response.status_code == 404

    def test_post_sem_api_key_retorna_401(self, client) -> None:
        payload = {
            "texto": "teste integracao",
            "sentimento": "positivo",
            "autor": "Cliente Shopee #0001",
            "aspectos": [],
        }
        response = client.post("/api/v1/avaliacoes", json=payload)
        assert response.status_code == 401

    def test_post_com_api_key_retorna_201(self, client, auth_headers) -> None:
        payload = {
            "texto": "teste integracao autenticado",
            "sentimento": "positivo",
            "autor": "Cliente Shopee #0001",
            "aspectos": [],
        }
        response = client.post("/api/v1/avaliacoes", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["texto"] == "teste integracao autenticado"

    def test_put_e_delete_com_api_key(self, client, auth_headers) -> None:
        create_payload = {
            "texto": "para editar",
            "sentimento": "neutro",
            "autor": "Cliente Shopee #0002",
            "aspectos": [],
        }
        created = client.post(
            "/api/v1/avaliacoes", json=create_payload, headers=auth_headers
        ).json()
        review_id = created["id"]

        update_response = client.put(
            f"/api/v1/avaliacoes/{review_id}",
            json={"sentimento": "negativo"},
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["sentimento"] == "negativo"

        delete_response = client.delete(
            f"/api/v1/avaliacoes/{review_id}", headers=auth_headers
        )
        assert delete_response.status_code == 204
        assert client.get(f"/api/v1/avaliacoes/{review_id}").status_code == 404


@pytest.mark.integration
class TestDashboardEndpoints:
    def test_dashboard_completo(self, client) -> None:
        response = client.get("/api/v1/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["total_avaliacoes"] == 5
        assert len(data["distribuicao_sentimento"]) >= 2
        assert len(data["sentimento_por_aspecto"]) == 3

    def test_dashboard_filtrado_por_periodo(self, client) -> None:
        response = client.get("/api/v1/dashboard?periodo_promocional=double_date")
        assert response.status_code == 200
        data = response.json()
        assert data["periodo_promocional"] == "double_date"
        assert data["total_avaliacoes"] == 5

    def test_resumo(self, client) -> None:
        response = client.get("/api/v1/dashboard/resumo")
        assert response.status_code == 200
        assert response.json()["total_reviews"] == 5


@pytest.mark.integration
class TestReviewsLegacyEndpoints:
    def test_listar_reviews_legado(self, client) -> None:
        response = client.get("/api/v1/reviews?page_size=3")
        assert response.status_code == 200
        assert response.json()["total"] == 5

    def test_stats_legado(self, client) -> None:
        response = client.get("/api/v1/reviews/stats")
        assert response.status_code == 200
        assert "por_sentimento" in response.json()
