from datetime import datetime, timedelta
from typing import Callable

from ..dominio.disputa import Disputa
from ..dominio.errores import PlazoVencido
from ..dominio.repositorios import DisputaRepository, SesionRepository
from .dtos import DisputaDTO, ReportarDisputa
from .unit_of_work import UnitOfWork


class DisputaApplicationService:
    def __init__(self, disputas: DisputaRepository, sesiones: SesionRepository,
                 uow: UnitOfWork, reloj: Callable[[], datetime] = datetime.now):
        self._disputas, self._sesiones, self._uow, self._reloj = disputas, sesiones, uow, reloj

    def reportarDisputa(self, cmd: ReportarDisputa) -> DisputaDTO:
        """CU-04a: una disputa se admite dentro de 24 horas desde el fin de la sesión (BR-0007)."""
        ahora = self._reloj()
        self._uow.begin()
        try:
            sesion = self._sesiones.obtenerPorId(cmd.sesionId)
            if ahora - sesion.horario.fin > timedelta(hours=24):
                raise PlazoVencido("La ventana de 24 horas para disputar terminó (BR-0007)")
            disputa = Disputa.abrir(cmd.sesionId, cmd.parte, ahora)
            self._disputas.actualizar(disputa)  # actualizar() hace upsert: el contrato solo define este método
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return DisputaDTO(disputa.idDisputa, disputa.estado.value)

    def resolverDisputa(self, idDisputa: str, idResponsableSoporte: str, decision: str,
                        evidenciaAdjunta) -> DisputaDTO:
        """DS-01 (CU-04c). La evidencia se incorporó antes con CU-04b; el parámetro `evidenciaAdjunta`
        se conserva por el contrato de la Etapa 4. La regla BR-0020 la aplica Disputa.resolver."""
        self._uow.begin()
        try:
            disputa = self._disputas.obtenerPorId(idDisputa)
            disputa.resolver(decision, idResponsableSoporte)  # lanza EVIDENCIA_REQUERIDA si falta evidencia
            self._disputas.actualizar(disputa)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return DisputaDTO(disputa.idDisputa, disputa.estado.value)
