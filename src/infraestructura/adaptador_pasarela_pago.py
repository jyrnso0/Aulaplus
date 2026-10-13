from ..aplicacion.dtos import ComprobantePago, DatosPago
from ..aplicacion.pasarela_pago_externa import PasarelaPagoExterna


class AdaptadorPasarelaPago(PasarelaPagoExterna):
    """Simula al proveedor de cobro: acepta cualquier referencia. Aquí iría la llamada real al proveedor."""

    def confirmarCobro(self, datosPago: DatosPago) -> ComprobantePago:
        return ComprobantePago(referencia=datosPago.referenciaCobro, importe=datosPago.importe)
