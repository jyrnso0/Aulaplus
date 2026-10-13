"""Interfaces de Repository. Viven en el Dominio, hablan en términos del negocio y no conocen SQL."""
from abc import ABC, abstractmethod
from datetime import datetime

from .disputa import Disputa
from .pago import Pago
from .reserva import Reserva
from .sesion import Sesion
from .tutor import Tutor


class ReservaRepository(ABC):
    @abstractmethod
    def obtenerPorId(self, id: str) -> Reserva: ...
    @abstractmethod
    def guardar(self, reserva: Reserva) -> None: ...
    @abstractmethod
    def pendientesVencidas(self, ahora: datetime) -> list[Reserva]: ...


class SesionRepository(ABC):
    @abstractmethod
    def obtenerPorId(self, id: str) -> Sesion: ...
    @abstractmethod
    def obtenerSesionesConfirmadasPorTutor(self, tutorId: str) -> list[Sesion]: ...
    @abstractmethod
    def guardar(self, sesion: Sesion) -> None: ...


class TutorRepository(ABC):
    @abstractmethod
    def obtenerPorId(self, id: str) -> Tutor: ...
    @abstractmethod
    def guardar(self, tutor: Tutor) -> None: ...


class PagoRepository(ABC):
    @abstractmethod
    def porReserva(self, reservaId: str) -> Pago: ...
    @abstractmethod
    def guardar(self, pago: Pago) -> None: ...


class DisputaRepository(ABC):
    @abstractmethod
    def obtenerPorId(self, id: str) -> Disputa: ...
    @abstractmethod
    def actualizar(self, disputa: Disputa) -> None: ...
