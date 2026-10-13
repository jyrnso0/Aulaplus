from datetime import datetime
from typing import Callable

from ..dominio.objetos_valor import Rol
from ..dominio.repositorios import SesionRepository
from ..dominio.servicios import PoliticaDeReembolso
from .dtos import ComprobanteCancelacionDTO
from .unit_of_work import UnitOfWork


class SesionApplicationService:
    def __init__(self, sesiones: SesionRepository, politicaReembolso: PoliticaDeReembolso,
                 uow: UnitOfWork, reloj: Callable[[], datetime] = datetime.now):
        self._sesiones, self._politica, self._uow, self._reloj = sesiones, politicaReembolso, uow, reloj

    def _transaccion(self, idSesion: str, operacion):
        self._uow.begin()
        try:
            sesion = self._sesiones.obtenerPorId(idSesion)
            resultado = operacion(sesion)
            self._sesiones.guardar(sesion)
            self._uow.commit()
            return resultado
        except Exception:
            self._uow.rollback()
            raise

    def iniciarSesion(self, sesionId: str) -> None:
        self._transaccion(sesionId, lambda s: s.iniciar(self._reloj()))

    def confirmarChecklist(self, sesionId: str, parte: Rol) -> None:
        self._transaccion(sesionId, lambda s: s.confirmarChecklist(parte))

    def finalizarSesion(self, sesionId: str) -> None:
        self._transaccion(sesionId, lambda s: s.finalizar(self._reloj()))

    def cancelarSesion(self, idSesion: str, idUsuarioQueCancela: str, motivo: str) -> ComprobanteCancelacionDTO:
        """CU-03. Registra la cancelación en la Sesion. El monto a devolver lo calcula PoliticaDeReembolso
        (self._politica.calcularMonto) y requiere el importe del Pago: ver «Pendientes» del README."""
        solicitante = Rol.TUTOR if idUsuarioQueCancela.startswith("tutor") else Rol.ESTUDIANTE
        cancelacion = self._transaccion(idSesion, lambda s: s.cancelar(solicitante, self._reloj()))
        return ComprobanteCancelacionDTO(idSesion, solicitante.value, cancelacion.esTardia)
