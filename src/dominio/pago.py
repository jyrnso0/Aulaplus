from uuid import uuid4

from .errores import EstadoInvalido
from .eventos import ConEventos
from .objetos_valor import Cancelacion, DesglosePago, Dinero, EstadoPago, Penalizacion


class Pago(ConEventos):
    """Aggregate root. Administra el importe, el desglose 20/80 (BR-0005) y las penalizaciones."""

    COMISION = "0.20"
    PENALIZACION_TARDIA = "0.50"

    def __init__(self, reservaId: str, importe: Dinero):
        self.idPago = str(uuid4())
        self.reservaId = reservaId
        self.importe = importe
        self.estado = EstadoPago.PENDIENTE
        self.desglose: DesglosePago | None = None
        self.comprobante: str | None = None

    def confirmar(self, comprobante: str) -> None:
        """Registra el cobro y el desglose 20/80 (ADR-05)."""
        if self.estado is not EstadoPago.PENDIENTE:
            raise EstadoInvalido("El pago ya fue confirmado")
        comision = self.importe.por(self.COMISION)
        self.desglose = DesglosePago(comision=comision, paraTutor=self.importe - comision)
        self.comprobante = comprobante
        self.estado = EstadoPago.CONFIRMADO
        self._registrar("PagoConfirmado", idPago=self.idPago, reservaId=self.reservaId)
        self._registrar("ComisionCalculada", comision=str(comision.monto))

    def aplicarCancelacion(self, cancelacion: Cancelacion) -> None:
        """BR-0004: penalización del 50% a quien cancela con menos de 4 horas de anticipación."""
        if cancelacion.esTardia:
            cancelacion.penalizacion = Penalizacion(self.importe.por(self.PENALIZACION_TARDIA), cancelacion.solicitante)

    def liquidar(self) -> DesglosePago:
        if self.estado is not EstadoPago.CONFIRMADO or self.desglose is None:
            raise EstadoInvalido("Solo un pago confirmado puede liquidarse")
        return self.desglose
