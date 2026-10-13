"""Value Objects y enumeraciones del dominio (inmutables, sin identidad)."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional


class Rol(Enum):
    ESTUDIANTE = "estudiante"
    TUTOR = "tutor"
    SOPORTE = "soporte"
    SISTEMA = "sistema"


class EstadoReserva(Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    LIBERADA = "liberada"


class EstadoSesion(Enum):
    PROGRAMADA = "programada"
    EN_CURSO = "en_curso"
    REALIZADA = "realizada"
    CANCELADA = "cancelada"


class EstadoPago(Enum):
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"


class EstadoDisputa(Enum):
    ESCALADA = "escalada"
    RESUELTA = "resuelta"


class EstadoCuenta(Enum):
    ACTIVO = "activo"
    SUSPENDIDO = "suspendido"


@dataclass(frozen=True)
class Dinero:
    """Importe en MXN con precisión decimal. El criterio de redondeo está pendiente de validar."""
    monto: Decimal

    def __post_init__(self):
        object.__setattr__(self, "monto", Decimal(self.monto).quantize(Decimal("0.01"), ROUND_HALF_UP))

    def por(self, porcentaje) -> "Dinero":
        return Dinero(self.monto * Decimal(str(porcentaje)))

    def __add__(self, otro: "Dinero") -> "Dinero":
        return Dinero(self.monto + otro.monto)

    def __sub__(self, otro: "Dinero") -> "Dinero":
        return Dinero(self.monto - otro.monto)


@dataclass(frozen=True)
class Horario:
    """Intervalo [inicio, fin): una sesión puede empezar exactamente cuando termina otra."""
    inicio: datetime
    fin: datetime

    def __post_init__(self):
        if self.fin <= self.inicio:
            raise ValueError("El fin del horario debe ser posterior al inicio")

    def traslapaCon(self, otro: "Horario") -> bool:
        return self.inicio < otro.fin and otro.inicio < self.fin


@dataclass(frozen=True)
class PlazoDePago:
    """BR-0001: la reserva vive 15 minutos esperando el pago."""
    venceEn: datetime

    def estaVencido(self, ahora: datetime) -> bool:
        return ahora > self.venceEn


@dataclass(frozen=True)
class DesglosePago:
    """BR-0005: comisión fija del 20% y 80% a favor del tutor."""
    comision: Dinero
    paraTutor: Dinero


@dataclass(frozen=True)
class Penalizacion:
    monto: Dinero
    cobradaA: Rol


@dataclass
class Cancelacion:
    """Quién cancela y con cuánta anticipación (BR-0004). Contiene la penalización aplicable."""
    solicitante: Rol
    anticipacion: timedelta
    penalizacion: Optional[Penalizacion] = None

    LIMITE_PENALIZACION = timedelta(hours=4)

    @property
    def esTardia(self) -> bool:
        return self.anticipacion < self.LIMITE_PENALIZACION


@dataclass(frozen=True)
class EvidenciaAdjunta:
    referencia: str
