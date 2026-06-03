"""Modelo de análise por aspecto."""

from dataclasses import dataclass
from typing import Any


@dataclass
class AspectoAnalise:
    """Sentimento associado a um aspecto (preço, entrega, qualidade)."""

    nome: str
    sentimento: str

    def to_dict(self) -> dict[str, str]:
        return {"nome": self.nome, "sentimento": self.sentimento}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AspectoAnalise":
        return cls(nome=data["nome"], sentimento=data["sentimento"])
