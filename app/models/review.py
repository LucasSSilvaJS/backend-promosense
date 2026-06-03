"""Entidade de domínio Avaliação (review Shopee, anotação manual)."""

from dataclasses import dataclass, field
from typing import Any

from app.constants.dataset import FONTE_ANOTACAO, PLATAFORMA
from app.models.aspecto import AspectoAnalise


@dataclass
class Review:
    """Avaliação real Shopee com sentimento anotado manualmente."""

    texto: str
    sentimento: str
    id: str | None = None
    autor: str | None = None
    plataforma: str = PLATAFORMA
    fonte_anotacao: str = FONTE_ANOTACAO
    periodo_promocional: str | None = None
    data_avaliacao: str | None = None
    aspectos: list[AspectoAnalise] = field(default_factory=list)
    aspecto: str | None = None
    sentimento_aspecto: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Review":
        doc_id = data.get("_id") or data.get("id")
        aspectos_raw = data.get("aspectos") or []
        aspectos = [
            AspectoAnalise.from_dict(a) if isinstance(a, dict) else a
            for a in aspectos_raw
        ]
        return cls(
            id=str(doc_id) if doc_id is not None else None,
            texto=data["texto"],
            sentimento=data["sentimento"],
            autor=data.get("autor"),
            plataforma=data.get("plataforma", PLATAFORMA),
            fonte_anotacao=data.get("fonte_anotacao", FONTE_ANOTACAO),
            periodo_promocional=data.get("periodo_promocional"),
            data_avaliacao=data.get("data_avaliacao"),
            aspectos=aspectos,
            aspecto=data.get("aspecto") or None,
            sentimento_aspecto=data.get("sentimento_aspecto") or None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "texto": self.texto,
            "sentimento": self.sentimento,
            "autor": self.autor,
            "plataforma": self.plataforma,
            "fonte_anotacao": self.fonte_anotacao,
            "periodo_promocional": self.periodo_promocional,
            "data_avaliacao": self.data_avaliacao,
            "aspectos": [a.to_dict() for a in self.aspectos],
            **(
                {"aspecto": self.aspecto, "sentimento_aspecto": self.sentimento_aspecto}
                if self.aspecto
                else {}
            ),
        }
