from datetime import datetime, timedelta
from typing import Optional

from .eventos import ConEventos
from .objetos_valor import EstadoCuenta


class DisponibilidadMateria:
    """Entidad interna del Tutor: disponibilidad independiente por materia (BR-0015)."""

    def __init__(self, materia: str, franjas: list):
        self.materia = materia
        self.franjas = list(franjas)


class Tutor(ConEventos):
    """Aggregate root. Protege su suspensión automática (BR-0018)."""

    MAX_AUSENCIAS = 2
    VENTANA_AUSENCIAS = timedelta(days=30)

    def __init__(self, idTutor: str):
        self.idTutor = idTutor
        self.estado = EstadoCuenta.ACTIVO
        self.disponibilidad: dict[str, DisponibilidadMateria] = {}
        self.ausencias: list[tuple[str, datetime]] = []

    def definirDisponibilidad(self, materia: str, franjas: list) -> None:
        self.disponibilidad[materia] = DisponibilidadMateria(materia, franjas)
        self._registrar("DisponibilidadActualizada", idTutor=self.idTutor, materia=materia)

    def registrarAusencia(self, sesionId: str, ahora: Optional[datetime] = None) -> bool:
        """Registra una falta; con más de 2 en 30 días el tutor se suspende. Devuelve True si se suspendió."""
        ahora = ahora or datetime.now()
        self.ausencias.append((sesionId, ahora))
        recientes = [a for a in self.ausencias if ahora - a[1] <= self.VENTANA_AUSENCIAS]
        if len(recientes) > self.MAX_AUSENCIAS and self.estado is EstadoCuenta.ACTIVO:
            self.estado = EstadoCuenta.SUSPENDIDO
            self._registrar("TutorSuspendido", idTutor=self.idTutor)
            return True
        return False
