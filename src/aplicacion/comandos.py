"""CQRS (Etapa 6): Commands y Handlers de escritura. Los Handlers delegan en el Application Service,
que es el punto de entrada de cada Command (ReservaApplicationService, DisputaApplicationService)."""
from dataclasses import dataclass

from .disputa_application_service import DisputaApplicationService
from .dtos import DatosPago, DisputaDTO, ReservaDTO
from .reserva_application_service import ReservaApplicationService


@dataclass(frozen=True)
class ConfirmarPagoReservaCommand:
    idReserva: str
    datosPago: DatosPago


@dataclass(frozen=True)
class ResolverDisputaCommand:
    idDisputa: str
    idResponsableSoporte: str
    decision: str
    evidenciaAdjunta: object = None


class ConfirmarPagoReservaCommandHandler:
    def __init__(self, servicio: ReservaApplicationService):
        self._servicio = servicio

    def handle(self, cmd: ConfirmarPagoReservaCommand) -> ReservaDTO:
        return self._servicio.confirmarPagoReserva(cmd.idReserva, cmd.datosPago)


class ResolverDisputaCommandHandler:
    def __init__(self, servicio: DisputaApplicationService):
        self._servicio = servicio

    def handle(self, cmd: ResolverDisputaCommand) -> DisputaDTO:
        return self._servicio.resolverDisputa(cmd.idDisputa, cmd.idResponsableSoporte, cmd.decision, cmd.evidenciaAdjunta)
