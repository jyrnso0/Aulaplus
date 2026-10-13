"""CQRS (Etapa 6): Queries, DTOs de lectura y Handlers. No usan Repository ni UnitOfWork,
leen de un read model (en producción, vistas o consultas sobre las mismas tablas)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class DashboardSemanalViewDTO:
    desde: date
    hasta: date
    totalComisiones: Decimal
    sesionesRealizadas: int
    cancelacionesTotales: int
    cancelacionesTardias: int
    disputasAbiertas: int
    disputasEscaladas: int
    disputasResueltas: int
    calificacionPromedio: float


@dataclass(frozen=True)
class PerfilTutorViewDTO:
    """Deja fuera a propósito el estado de cuenta, el historial de ausencias y los datos de pago."""
    idTutor: str
    nombre: str
    materias: list
    modalidades: list
    calificacionPromedio: float
    totalCalificaciones: int
    franjasDisponibles: list


class DashboardReadModel(ABC):
    @abstractmethod
    def totalesSemana(self, desde: date, hasta: date) -> DashboardSemanalViewDTO: ...


class PerfilTutorReadModel(ABC):
    @abstractmethod
    def perfil(self, idTutor: str) -> PerfilTutorViewDTO: ...


@dataclass(frozen=True)
class ConsultarDashboardSemanalQuery:
    rangoFechas: tuple
    idAdministrador: str


@dataclass(frozen=True)
class ConsultarPerfilTutorQuery:
    idTutor: str


class ConsultarDashboardSemanalQueryHandler:
    def __init__(self, readModel: DashboardReadModel):
        self._readModel = readModel

    def handle(self, query: ConsultarDashboardSemanalQuery) -> DashboardSemanalViewDTO:
        desde, hasta = query.rangoFechas
        return self._readModel.totalesSemana(desde, hasta)


class ConsultarPerfilTutorQueryHandler:
    def __init__(self, readModel: PerfilTutorReadModel):
        self._readModel = readModel

    def handle(self, query: ConsultarPerfilTutorQuery) -> PerfilTutorViewDTO:
        return self._readModel.perfil(query.idTutor)
