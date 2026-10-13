"""Raíz de composición: aquí (y solo aquí) se eligen las implementaciones concretas."""
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from ..aplicacion.disputa_application_service import DisputaApplicationService
from ..aplicacion.reserva_application_service import ReservaApplicationService
from ..aplicacion.sesion_application_service import SesionApplicationService
from ..aplicacion.tutor_application_service import TutorApplicationService
from ..dominio.servicios import PoliticaDeReembolso, ValidadorTraslapeHorario
from .adaptador_pasarela_pago import AdaptadorPasarelaPago
from .almacen import Almacen
from .sql_repositorios import (SqlDisputaRepository, SqlPagoRepository, SqlReservaRepository,
                               SqlSesionRepository, SqlTutorRepository)
from .sql_unit_of_work import SqlUnitOfWork


@dataclass
class Contenedor:
    almacen: Almacen
    reservas: ReservaApplicationService
    tutores: TutorApplicationService
    sesiones: SesionApplicationService
    disputas: DisputaApplicationService
    repo_reservas: SqlReservaRepository
    repo_sesiones: SqlSesionRepository
    repo_tutores: SqlTutorRepository
    repo_pagos: SqlPagoRepository
    repo_disputas: SqlDisputaRepository


def crearContenedor(reloj: Callable[[], datetime] = datetime.now) -> Contenedor:
    a = Almacen()
    uow = SqlUnitOfWork(a)
    rr, sr, tr, pr, dr = (SqlReservaRepository(a), SqlSesionRepository(a), SqlTutorRepository(a),
                          SqlPagoRepository(a), SqlDisputaRepository(a))
    return Contenedor(
        almacen=a,
        reservas=ReservaApplicationService(rr, sr, pr, ValidadorTraslapeHorario(), AdaptadorPasarelaPago(), uow, reloj),
        tutores=TutorApplicationService(tr, uow),
        sesiones=SesionApplicationService(sr, PoliticaDeReembolso(), uow, reloj),
        disputas=DisputaApplicationService(dr, sr, uow, reloj),
        repo_reservas=rr, repo_sesiones=sr, repo_tutores=tr, repo_pagos=pr, repo_disputas=dr,
    )
