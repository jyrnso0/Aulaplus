"""Eventos de dominio: hechos que ya ocurrieron. Cada aggregate los acumula en `eventos`."""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EventoDeDominio:
    nombre: str
    datos: dict[str, Any] = field(default_factory=dict)


class ConEventos:
    """Comportamiento común de las raíces de aggregate."""

    def _registrar(self, nombre: str, **datos: Any) -> None:
        if not hasattr(self, "eventos"):
            self.eventos: list[EventoDeDominio] = []
        self.eventos.append(EventoDeDominio(nombre, datos))

    def extraerEventos(self) -> list[EventoDeDominio]:
        eventos = list(getattr(self, "eventos", []))
        self.eventos = []
        return eventos
