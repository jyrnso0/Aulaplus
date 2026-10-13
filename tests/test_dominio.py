"""Reglas que viven en el dominio (no en los servicios)."""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from aulaplus.dominio.errores import EstadoInvalido
from aulaplus.dominio.objetos_valor import Dinero, Rol
from aulaplus.dominio.pago import Pago
from aulaplus.dominio.servicios import PoliticaDeReembolso
from aulaplus.dominio.sesion import Sesion
from aulaplus.dominio.tutor import Tutor
from aulaplus.dominio.objetos_valor import EstadoCuenta, Horario


def _sesion():
    ini = datetime(2026, 10, 21, 10, 0)
    return Sesion("r1", "t1", Horario(ini, ini + timedelta(hours=1)))


def test_cancelacion_con_menos_de_4_horas_aplica_penalizacion_del_50():
    sesion = _sesion()
    cancelacion = sesion.cancelar(Rol.ESTUDIANTE, sesion.horario.inicio - timedelta(hours=3))   # BR-0004
    assert cancelacion.esTardia
    pago = Pago("r1", Dinero(Decimal("100")))
    pago.aplicarCancelacion(cancelacion)
    assert cancelacion.penalizacion.monto.monto == Decimal("50.00")
    assert cancelacion.penalizacion.cobradaA is Rol.ESTUDIANTE


def test_cancelacion_con_anticipacion_no_se_penaliza():
    sesion = _sesion()
    cancelacion = sesion.cancelar(Rol.ESTUDIANTE, sesion.horario.inicio - timedelta(hours=5))
    assert not cancelacion.esTardia
    assert PoliticaDeReembolso().calcularMonto("cancelacion", cancelacion, Dinero(Decimal("100"))).monto == Decimal("100.00")


def test_politica_de_reembolso_tardia_y_ausencia_del_tutor():
    sesion = _sesion()
    tardia = sesion.cancelar(Rol.ESTUDIANTE, sesion.horario.inicio - timedelta(hours=1))
    politica = PoliticaDeReembolso()
    assert politica.calcularMonto("cancelacion", tardia, Dinero(Decimal("100"))).monto == Decimal("50.00")
    assert politica.calcularMonto("ausencia_tutor", tardia, Dinero(Decimal("100"))).monto == Decimal("100.00")  # BR-0009


def test_no_se_finaliza_sin_checklist_de_ambos():
    sesion = _sesion()
    sesion.iniciar(sesion.horario.inicio)
    sesion.confirmarChecklist(Rol.TUTOR)
    with pytest.raises(EstadoInvalido):                                # BR-0014
        sesion.finalizar(sesion.horario.fin)
    sesion.confirmarChecklist(Rol.ESTUDIANTE)
    sesion.finalizar(sesion.horario.fin)


def test_suspension_con_mas_de_dos_ausencias_en_30_dias():
    tutor = Tutor("t1")
    ahora = datetime(2026, 10, 1)
    assert not tutor.registrarAusencia("s1", ahora)
    assert not tutor.registrarAusencia("s2", ahora + timedelta(days=1))   # la segunda no suspende
    assert tutor.registrarAusencia("s3", ahora + timedelta(days=2))       # la tercera sí (BR-0018)
    assert tutor.estado is EstadoCuenta.SUSPENDIDO


def test_horario_semiabierto():
    a = Horario(datetime(2026, 1, 1, 10), datetime(2026, 1, 1, 11))
    assert not a.traslapaCon(Horario(datetime(2026, 1, 1, 11), datetime(2026, 1, 1, 12)))
    assert a.traslapaCon(Horario(datetime(2026, 1, 1, 10, 30), datetime(2026, 1, 1, 11, 30)))
