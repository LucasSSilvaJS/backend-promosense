"""Testes de sistema — fluxo completo da API PromoSense."""

import pytest


AVALIACAO_PAYLOAD = {
    "texto": "Double Date com entrega no prazo e preco bom",
    "sentimento": "positivo",
    "autor": "Cliente Shopee #0100",
    "periodo_promocional": "double_date_2025",
    "data_avaliacao": "2025-08-08",
    "aspectos": [
        {"nome": "preco", "sentimento": "positivo"},
        {"nome": "entrega", "sentimento": "positivo"},
        {"nome": "qualidade", "sentimento": "neutro"},
    ],
}


@pytest.mark.system
class TestFluxoCompletoPromoSense:
    def test_jornada_consulta_front(self, client) -> None:
        """Simula o front: health → dataset → periodos → listagem → detalhe → dashboard."""
        health = client.get("/api/v1/health")
        assert health.json()["status"] == "ok"

        dataset = client.get("/api/v1/dataset")
        assert dataset.json()["plataforma"] == "shopee"

        periodos = client.get("/api/v1/avaliacoes/periodos")
        periodo_id = periodos.json()["items"][0]["id"]

        lista = client.get(
            f"/api/v1/avaliacoes?periodo_promocional={periodo_id}&page_size=10"
        )
        assert lista.status_code == 200
        assert lista.json()["total"] >= 1

        primeiro_id = lista.json()["items"][0]["id"]
        detalhe = client.get(f"/api/v1/avaliacoes/{primeiro_id}")
        assert detalhe.status_code == 200
        assert len(detalhe.json()["aspectos"]) == 3

        dashboard = client.get(f"/api/v1/dashboard?periodo_promocional={periodo_id}")
        assert dashboard.status_code == 200
        assert dashboard.json()["total_avaliacoes"] >= 1

    def test_jornada_crud_admin(self, client, auth_headers) -> None:
        """Simula operacoes administrativas: criar → consultar → editar → excluir."""
        create = client.post(
            "/api/v1/avaliacoes", json=AVALIACAO_PAYLOAD, headers=auth_headers
        )
        assert create.status_code == 201
        review_id = create.json()["id"]

        read = client.get(f"/api/v1/avaliacoes/{review_id}")
        assert read.json()["periodo_label"] == "Double Date 2025"
        assert read.json()["aspectos"][0]["label"] == "Preço"

        update = client.put(
            f"/api/v1/avaliacoes/{review_id}",
            json={"sentimento": "negativo", "texto": "texto atualizado no sistema"},
            headers=auth_headers,
        )
        assert update.status_code == 200
        assert update.json()["sentimento"] == "negativo"

        delete = client.delete(f"/api/v1/avaliacoes/{review_id}", headers=auth_headers)
        assert delete.status_code == 204
        assert client.get(f"/api/v1/avaliacoes/{review_id}").status_code == 404

    def test_busca_por_texto(self, client) -> None:
        response = client.get("/api/v1/avaliacoes?search=entrega")
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_headers_seguranca(self, client) -> None:
        response = client.get("/api/v1/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
