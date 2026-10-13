from datetime import datetime
from uuid import uuid4

from .errores import EstadoInvalido
from .eventos import ConEventos
from .objetos_valor import Cancelacion, EstadoSesion, Horario, Rol


class Sesion(ConEventos):
    """Aggregate root. Nace al confirmarse el pago de una Reserva."""

    def __init__(self, reservaId: str, tutorId: str, horario: Horario):
        self.idSesion = str(uuid4())
        self.reservaId = reservaId
        self.tutorId = tutorId
        self.horario = horario
        self.estado = EstadoSesion.PROGRAMADA
        self.checklist: set[Rol] = set()
        self._registrar("SesionProgramada", idSesion=self.idSesion, reservaId=reservaId)

    def iniciar(self, ahora: datetime) -> None:
        if self.estado is not EstadoSesion.PROGRAMADA:
            raise EstadoInvalido("Solo una sesión programada puede iniciar")
        self.estado = EstadoSesion.EN_CURSO
        self.inicioReal = ahora

    def confirmarChecklist(self, parte: Rol) -> None:
        if self.estado is not EstadoSesion.EN_CURSO:
            raise EstadoInvalido("El checklist se confirma durante la sesión")
        self.checklist.add(parte)

    def finalizar(self, ahora: datetime) -> None:
        """BR-0014: no se da por realizada sin el checklist de ambas partes."""
        if self.estado is not EstadoSesion.EN_CURSO:
            raise EstadoInvalido("Solo una sesión en curso puede finalizar")
        if not {Rol.ESTUDIANTE, Rol.TUTOR} <= self.checklist:
            raise EstadoInvalido("Falta el checklist de una de las partes (BR-0014)")
        self.estado = EstadoSesion.REALIZADA
        self.finReal = ahora
        self._registrar("SesionRealizada", idSesion=self.idSesion)

    def cancelar(self, solicitante: Rol, ahora: datetime) -> Cancelacion:
        """Registra quién cancela y con qué anticipación (BR-0004). El monto lo decide el servicio de dominio."""
        if self.estado is not EstadoSesion.PROGRAMADA:
            raise EstadoInvalido("Solo una sesión programada puede cancelarse")
        self.estado = EstadoSesion.CANCELADA
        cancelacion = Cancelacion(solicitante, self.horario.inicio - ahora)
        self._registrar("SesionCancelada", idSesion=self.idSesion, tardia=cancelacion.esTardia)
        return cancelacion
