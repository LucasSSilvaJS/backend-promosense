"""Serviço de negócio para avaliações (CRUD + consultas PromoSense)."""

from app.constants.promosense import ASPECTOS
from app.models.aspecto import AspectoAnalise
from app.models.review import Review
from app.repositories.review_repository import JsonReviewRepository
from app.schemas.review import (
    AvaliacaoCreateSchema,
    AvaliacaoListSchema,
    AvaliacaoSchema,
    AvaliacaoUpdateSchema,
    DashboardSchema,
    DatasetInfoSchema,
    PeriodoListSchema,
    PeriodoSchema,
    ReviewListSchema,
    ReviewSchema,
    ReviewStatsSchema,
    SentimentoCountSchema,
    AspectoStatsGroupSchema,
    build_aspecto_schemas,
    dataset_info,
    periodo_label,
)
from app.utils.enrichment import _build_aspectos


class ReviewService:
    """Orquestra CRUD e consultas entre API e repositório JSON."""

    def __init__(self, repository: JsonReviewRepository) -> None:
        self._repository = repository

    def _to_schema(self, review: Review) -> AvaliacaoSchema:
        aspectos = review.aspectos
        if not aspectos:
            aspectos = _build_aspectos(
                review.texto, review.sentimento, review.id or "0"
            )
        return AvaliacaoSchema(
            id=review.id or "",
            texto=review.texto,
            sentimento=review.sentimento,  # type: ignore[arg-type]
            autor=review.autor or "Cliente Shopee",
            plataforma=review.plataforma,
            fonte_anotacao=review.fonte_anotacao,
            periodo_promocional=review.periodo_promocional,  # type: ignore[arg-type]
            periodo_label=periodo_label(review.periodo_promocional),
            data_avaliacao=review.data_avaliacao or "",
            aspectos=build_aspecto_schemas(aspectos),
        )

    def list_periodos(self) -> PeriodoListSchema:
        return PeriodoListSchema(
            items=[PeriodoSchema(**p) for p in self._repository.list_periodos()]
        )

    def get_dataset_info(self) -> DatasetInfoSchema:
        return dataset_info(total=self._repository.count())

    def create(self, payload: AvaliacaoCreateSchema) -> AvaliacaoSchema:
        aspectos = [
            AspectoAnalise(nome=a.nome, sentimento=a.sentimento)
            for a in payload.aspectos
        ]
        if not aspectos:
            aspectos = _build_aspectos(
                payload.texto, payload.sentimento, "new"
            )

        review = Review(
            texto=payload.texto,
            sentimento=payload.sentimento,
            autor=payload.autor,
            plataforma=payload.plataforma,
            fonte_anotacao=payload.fonte_anotacao,
            periodo_promocional=payload.periodo_promocional,
            data_avaliacao=payload.data_avaliacao,
            aspectos=aspectos,
        )
        created = self._repository.create(review)
        return self._to_schema(created)

    def get_by_id(self, review_id: str) -> AvaliacaoSchema | None:
        review = self._repository.find_by_id(review_id)
        return self._to_schema(review) if review else None

    def list_reviews(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        sentimento: str | None = None,
        periodo_promocional: str | None = None,
        search: str | None = None,
    ) -> AvaliacaoListSchema:
        items, total = self._repository.find_all(
            page=page,
            page_size=page_size,
            sentimento=sentimento,
            periodo_promocional=periodo_promocional,
            search=search,
        )
        return AvaliacaoListSchema(
            total=total,
            page=page,
            page_size=page_size,
            periodo_promocional=periodo_promocional,
            items=[self._to_schema(r) for r in items],
        )

    def update(
        self, review_id: str, payload: AvaliacaoUpdateSchema
    ) -> AvaliacaoSchema | None:
        data = payload.model_dump(exclude_unset=True)
        if "aspectos" in data and data["aspectos"] is not None:
            data["aspectos"] = [
                {"nome": a["nome"], "sentimento": a["sentimento"]}
                if isinstance(a, dict)
                else {"nome": a.nome, "sentimento": a.sentimento}
                for a in data["aspectos"]
            ]
        updated = self._repository.update(review_id, data)
        return self._to_schema(updated) if updated else None

    def delete(self, review_id: str) -> bool:
        return self._repository.delete(review_id)

    def get_dashboard(self, periodo_promocional: str | None = None) -> DashboardSchema:
        from app.constants.promosense import ASPECTO_LABELS

        distribuicao = self._repository.stats_by_sentimento(periodo_promocional)
        por_aspecto = self._repository.stats_by_aspecto(periodo_promocional)

        return DashboardSchema(
            total_avaliacoes=self._repository.count(periodo_promocional),
            periodo_promocional=periodo_promocional,
            periodo_label=periodo_label(periodo_promocional),
            distribuicao_sentimento=[
                SentimentoCountSchema(**item) for item in distribuicao
            ],
            sentimento_por_aspecto=[
                AspectoStatsGroupSchema(
                    aspecto=nome,
                    label=ASPECTO_LABELS[nome],
                    distribuicao=[
                        SentimentoCountSchema(**s)
                        for s in por_aspecto.get(nome, [])
                    ],
                )
                for nome in ASPECTOS
            ],
        )

    def get_stats(self, periodo_promocional: str | None = None) -> ReviewStatsSchema:
        counts = self._repository.stats_by_sentimento(periodo_promocional)
        return ReviewStatsSchema(
            total_reviews=self._repository.count(periodo_promocional),
            por_sentimento=[
                SentimentoCountSchema(
                    sentimento=c["sentimento"],
                    total=c["total"],
                    percentual=c["percentual"],
                )
                for c in counts
            ],
        )

    # Compatibilidade com rota /reviews
    def list_reviews_legacy(self, **kwargs) -> ReviewListSchema:
        result = self.list_reviews(**kwargs)
        return ReviewListSchema(**result.model_dump())

    def get_by_id_legacy(self, review_id: str) -> ReviewSchema | None:
        item = self.get_by_id(review_id)
        return ReviewSchema(**item.model_dump()) if item else None
