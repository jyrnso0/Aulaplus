"""DTOs y Commands. No tienen reglas de negocio; solo transportan datos."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..dominio.objetos_valor import Horario, Rol


@dataclass(frozen=True)
class ReservarTutoria:  # Command (CU-01a)
    estudianteId: str
    tutorId: str
    horario: Horario
    importe: Decimal


@dataclass(frozen=True)
class ReportarDisputa:  # Command (CU-04a)
    sesionId: str
    parte: Rol


@dataclass(frozen=True)
class DatosPago:
    referenciaCobro: str
    importe: Decimal


@dataclass(frozen=True)
class ComprobantePago:
    referencia: str
    importe: Decimal


@dataclass(frozen=True)
class ReservaDTO:
    reservaId: str
    importe: Decimal
    estado: str
    venceEn: datetime
    sesionId: Optional[str] = None


@dataclass(frozen=True)
class DisputaDTO:
    disputaId: str
    estado: str


@dataclass(frozen=True)
class ConfirmacionDTO:
    idTutor: str
    materia: str


@dataclass(frozen=True)
class ComprobanteCancelacionDTO:
    idSesion: str
    solicitante: str
    tardia: bool
