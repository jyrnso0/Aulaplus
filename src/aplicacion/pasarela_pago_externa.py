from abc import ABC, abstractmethod

from .dtos import ComprobantePago, DatosPago


class PasarelaPagoExterna(ABC):
    """Puerto hacia el proveedor de cobro. La implementación vive en Infraestructura."""

    @abstractmethod
    def confirmarCobro(self, datosPago: DatosPago) -> ComprobantePago: ...
