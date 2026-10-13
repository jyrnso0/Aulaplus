from datetime import datetime
from uuid import uuid4

from .errores import EstadoInvalido, EvidenciaRequerida
from .eventos import ConEventos
from .objetos_valor import EstadoDisputa, EvidenciaAdjunta, Rol


class Disputa(ConEventos):
    """Aggregate root. BR-0020: no se resuelve sin evidencia, decisión y responsable."""

    def __init__(self, sesionId: str, parte: Rol, ahora: datetime):
        self.idDisputa = str(uuid4())
        self.sesionId = sesionId
        self.parte = parte
        self.escaladaEn = ahora  # el plazo de 48 h (BR-0011) corre desde el escalamiento
        self.estado = EstadoDisputa.ESCALADA
        self.evidencia: list[EvidenciaAdjunta] = []
        self.decision: str | None = None
        self.responsable: str | None = None
        self._registrar("DisputaReportada", idDisputa=self.idDisputa, sesionId=sesionId)
        self._registrar("DisputaEscalada", idDisputa=self.idDisputa)

    @classmethod
    def abrir(cls, sesionId: str, parte: Rol, ahora: datetime) -> "Disputa":
        return cls(sesionId, parte, ahora)

    def adjuntarEvidencia(self, referencia: str) -> None:
        self.evidencia.append(EvidenciaAdjunta(referencia))

    def resolver(self, decision: str, responsable: str) -> None:
        if self.estado is not EstadoDisputa.ESCALADA:
            raise EstadoInvalido("La disputa ya fue resuelta")
        if not self.evidencia or not decision or not responsable:
            raise EvidenciaRequerida("No se cierra sin evidencia, decisión y responsable (BR-0020)")
        self.decision = decision
        self.responsable = responsable
        self.estado = EstadoDisputa.RESUELTA
        self._registrar("DisputaResuelta", idDisputa=self.idDisputa, responsable=responsable)
