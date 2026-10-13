from datetime import datetime, timedelta
from uuid import uuid4

from .errores import EstadoInvalido
from .eventos import ConEventos
from .objetos_valor import Dinero, EstadoReserva, Horario, PlazoDePago


class Reserva(ConEventos):
    """Aggregate root. Controla el plazo de pago de 15 minutos (BR-0001)."""

    MINUTOS_PLAZO = 15

    def __init__(self, tutorId: str, estudianteId: str, horario: Horario, importe: Dinero, ahora: datetime):
        self.idReserva = str(uuid4())
        self.tutorId = tutorId
        self.estudianteId = estudianteId
        self.horario = horario
        self.importe = importe
        self.plazo = PlazoDePago(ahora + timedelta(minutes=self.MINUTOS_PLAZO))
        self.estado = EstadoReserva.PENDIENTE
        self._registrar("ReservaCreada", idReserva=self.idReserva, venceEn=self.plazo.venceEn)

    def confirmarPago(self, ahora: datetime) -> bool:
        """Confirma si el pago llegó a tiempo. Devuelve False si el plazo ya venció."""
        if self.estado is not EstadoReserva.PENDIENTE:
            raise EstadoInvalido(f"La reserva está {self.estado.value}")
        if self.plazo.estaVencido(ahora):
            return False
        self.estado = EstadoReserva.CONFIRMADA
        self._registrar("ReservaConfirmada", idReserva=self.idReserva)
        return True

    def liberarPorTimeout(self, ahora: datetime) -> bool:
        """Libera el horario si la reserva sigue pendiente y su plazo venció."""
        if self.estado is EstadoReserva.PENDIENTE and self.plazo.estaVencido(ahora):
            self.estado = EstadoReserva.LIBERADA
            self._registrar("ReservaLiberada", idReserva=self.idReserva)
            return True
        return False
