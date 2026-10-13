"""DS-02: flujo principal (CU-01). Reserva y confirmación de pago."""
from decimal import Decimal

import pytest

from aulaplus.aplicacion.dtos import DatosPago
from aulaplus.dominio.errores import HorarioNoDisponible, PlazoVencido
from aulaplus.dominio.objetos_valor import EstadoReserva, Horario


def test_flujo_completo_reserva_y_pago(app, reloj, comando):
    reserva = app.reservas.reservarTutoria(comando)
    assert reserva.estado == "pendiente"                      # BR-0001: nace pendiente...
    assert (reserva.venceEn - reloj()).seconds == 15 * 60     # ...con 15 minutos de plazo

    reloj.avanzar(minutes=10)
    resultado = app.reservas.confirmarPagoReserva(reserva.reservaId, DatosPago("cobro-1", Decimal("100")))

    assert resultado.estado == "confirmada" and resultado.sesionId
    pago = app.repo_pagos.porReserva(reserva.reservaId)
    assert pago.desglose.comision.monto == Decimal("20.00")   # BR-0005
    assert pago.desglose.paraTutor.monto == Decimal("80.00")
    eventos = [e.nombre for e in app.almacen.outbox]          # se publican después del commit
    assert {"ReservaConfirmada", "PagoConfirmado", "SesionProgramada"} <= set(eventos)


def test_pago_fuera_de_plazo_hace_rollback(app, reloj, comando):
    reserva = app.reservas.reservarTutoria(comando)
    reloj.avanzar(minutes=16)
    with pytest.raises(PlazoVencido):
        app.reservas.confirmarPagoReserva(reserva.reservaId, DatosPago("cobro-1", Decimal("100")))
    assert app.repo_reservas.obtenerPorId(reserva.reservaId).estado is EstadoReserva.PENDIENTE
    assert app.almacen.pagos == {} and app.almacen.sesiones == {}   # no se guardó nada


def test_traslape_se_rechaza_al_reservar(app, reloj, comando):
    primera = app.reservas.reservarTutoria(comando)
    app.reservas.confirmarPagoReserva(primera.reservaId, DatosPago("c1", Decimal("100")))
    with pytest.raises(HorarioNoDisponible):                        # BR-0006
        app.reservas.reservarTutoria(comando)


def test_sesiones_consecutivas_son_compatibles(app, comando, horario):
    primera = app.reservas.reservarTutoria(comando)
    app.reservas.confirmarPagoReserva(primera.reservaId, DatosPago("c1", Decimal("100")))
    siguiente = Horario(horario.fin, horario.fin.replace(hour=12))   # [10,11) y [11,12)
    app.reservas.reservarTutoria(type(comando)(comando.estudianteId, comando.tutorId, siguiente, comando.importe))


def test_traslape_se_revalida_al_confirmar_el_pago(app, comando):
    """Dos reservas pendientes pueden pedir el mismo horario: gana la primera que paga."""
    primera = app.reservas.reservarTutoria(comando)
    segunda = app.reservas.reservarTutoria(comando)
    app.reservas.confirmarPagoReserva(primera.reservaId, DatosPago("c1", Decimal("100")))
    with pytest.raises(HorarioNoDisponible):
        app.reservas.confirmarPagoReserva(segunda.reservaId, DatosPago("c2", Decimal("100")))
    assert app.repo_reservas.obtenerPorId(segunda.reservaId).estado is EstadoReserva.PENDIENTE


def test_liberar_reservas_vencidas(app, reloj, comando):
    reserva = app.reservas.reservarTutoria(comando)
    reloj.avanzar(minutes=20)
    assert app.reservas.liberarReservasVencidas() == 1
    assert app.repo_reservas.obtenerPorId(reserva.reservaId).estado is EstadoReserva.LIBERADA
