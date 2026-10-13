"""DS-01: flujo con regla y alternativa (CU-04c). BR-0020: no se cierra una disputa sin evidencia."""
from datetime import datetime
from decimal import Decimal

import pytest

from aulaplus.aplicacion.dtos import DatosPago, ReportarDisputa
from aulaplus.dominio.errores import EvidenciaRequerida, PlazoVencido
from aulaplus.dominio.objetos_valor import EstadoDisputa, Rol


@pytest.fixture
def disputa(app, comando, reloj):
    reserva = app.reservas.reservarTutoria(comando)
    sesion = app.reservas.confirmarPagoReserva(reserva.reservaId, DatosPago("c1", Decimal("100")))
    reloj.ahora = datetime(2026, 10, 21, 12, 0)   # una hora después de terminar la sesión
    return app.disputas.reportarDisputa(ReportarDisputa(sesion.sesionId, Rol.ESTUDIANTE))


def test_sin_evidencia_se_rechaza_y_no_cambia_nada(app, disputa):
    with pytest.raises(EvidenciaRequerida):
        app.disputas.resolverDisputa(disputa.disputaId, "soporte-1", "reembolso total", None)
    assert app.repo_disputas.obtenerPorId(disputa.disputaId).estado is EstadoDisputa.ESCALADA
    assert "DisputaResuelta" not in [e.nombre for e in app.almacen.outbox]


def test_con_evidencia_se_resuelve_y_publica_el_evento(app, disputa):
    app.repo_disputas.obtenerPorId(disputa.disputaId).adjuntarEvidencia("captura-1")   # CU-04b
    resultado = app.disputas.resolverDisputa(disputa.disputaId, "soporte-1", "reembolso total", "captura-1")
    assert resultado.estado == "resuelta"
    assert "DisputaResuelta" in [e.nombre for e in app.almacen.outbox]


def test_disputa_fuera_de_24_horas_se_rechaza(app, comando, reloj):
    reserva = app.reservas.reservarTutoria(comando)
    sesion = app.reservas.confirmarPagoReserva(reserva.reservaId, DatosPago("c1", Decimal("100")))
    reloj.ahora = datetime(2026, 10, 22, 12, 0)   # más de 24 h después del fin
    with pytest.raises(PlazoVencido):
        app.disputas.reportarDisputa(ReportarDisputa(sesion.sesionId, Rol.ESTUDIANTE))
