from datetime import datetime
from typing import Callable

from ..dominio.errores import PlazoVencido
from ..dominio.objetos_valor import Dinero
from ..dominio.pago import Pago
from ..dominio.repositorios import PagoRepository, ReservaRepository, SesionRepository
from ..dominio.reserva import Reserva
from ..dominio.servicios import ValidadorTraslapeHorario
from ..dominio.sesion import Sesion
from .dtos import DatosPago, ReservaDTO, ReservarTutoria
from .pasarela_pago_externa import PasarelaPagoExterna
from .unit_of_work import UnitOfWork


class ReservaApplicationService:
    """Coordina CU-01. No contiene reglas: las reglas viven en Reserva, Pago, Sesion y el validador."""

    def __init__(self, reservas: ReservaRepository, sesiones: SesionRepository, pagos: PagoRepository,
                 validador: ValidadorTraslapeHorario, pasarela: PasarelaPagoExterna,
                 uow: UnitOfWork, reloj: Callable[[], datetime] = datetime.now):
        self._reservas, self._sesiones, self._pagos = reservas, sesiones, pagos
        self._validador, self._pasarela, self._uow, self._reloj = validador, pasarela, uow, reloj

    def reservarTutoria(self, cmd: ReservarTutoria) -> ReservaDTO:
        """DS-02, fase 1 (CU-01a): valida el traslape y crea la reserva con plazo de 15 minutos."""
        ahora = self._reloj()
        self._uow.begin()
        try:
            sesiones = self._sesiones.obtenerSesionesConfirmadasPorTutor(cmd.tutorId)
            self._validador.verificarTraslape(cmd.horario, sesiones)
            reserva = Reserva(cmd.tutorId, cmd.estudianteId, cmd.horario, Dinero(cmd.importe), ahora)
            self._reservas.guardar(reserva)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return ReservaDTO(reserva.idReserva, reserva.importe.monto, reserva.estado.value, reserva.plazo.venceEn)

    def confirmarPagoReserva(self, idReserva: str, datosPago: DatosPago) -> ReservaDTO:
        """DS-02, fase 2 (CU-01b): cobra, confirma la reserva, registra el pago y programa la sesión
        en una sola transacción. Si algo falla antes del commit no se guarda nada."""
        ahora = self._reloj()
        self._uow.begin()
        try:
            reserva = self._reservas.obtenerPorId(idReserva)
            comprobante = self._pasarela.confirmarCobro(datosPago)
            if not reserva.confirmarPago(ahora):
                # Un cobro externo tardío no reactiva la reserva: se concilia aparte (ADR-06 / Etapa 4).
                raise PlazoVencido("El plazo de 15 minutos venció (BR-0001)")
            pago = Pago(reserva.idReserva, reserva.importe)
            pago.confirmar(comprobante.referencia)
            sesiones = self._sesiones.obtenerSesionesConfirmadasPorTutor(reserva.tutorId)
            self._validador.verificarTraslape(reserva.horario, sesiones)  # se revalida (BR-0006)
            sesion = Sesion(reserva.idReserva, reserva.tutorId, reserva.horario)
            self._reservas.guardar(reserva)
            self._pagos.guardar(pago)
            self._sesiones.guardar(sesion)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return ReservaDTO(reserva.idReserva, reserva.importe.monto, reserva.estado.value,
                          reserva.plazo.venceEn, sesion.idSesion)

    def liberarReservasVencidas(self) -> int:
        """CU-01c: libera los horarios de las reservas cuyo plazo venció sin pago."""
        ahora = self._reloj()
        self._uow.begin()
        try:
            liberadas = 0
            for reserva in self._reservas.pendientesVencidas(ahora):
                if reserva.liberarPorTimeout(ahora):
                    self._reservas.guardar(reserva)
                    liberadas += 1
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return liberadas
