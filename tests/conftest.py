from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from aulaplus.aplicacion.dtos import ReservarTutoria
from aulaplus.dominio.objetos_valor import Horario
from aulaplus.infraestructura.contenedor import crearContenedor


class RelojFijo:
    def __init__(self, ahora):
        self.ahora = ahora

    def __call__(self):
        return self.ahora

    def avanzar(self, **kw):
        self.ahora += timedelta(**kw)


@pytest.fixture
def reloj():
    return RelojFijo(datetime(2026, 10, 20, 9, 0))


@pytest.fixture
def app(reloj):
    return crearContenedor(reloj)


@pytest.fixture
def horario():
    return Horario(datetime(2026, 10, 21, 10, 0), datetime(2026, 10, 21, 11, 0))


@pytest.fixture
def comando(horario):
    return ReservarTutoria("est-1", "tutor-1", horario, Decimal("100"))
