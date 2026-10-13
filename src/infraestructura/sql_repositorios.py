"""Implementaciones de los Repository del Dominio. Hoy leen y escriben en el Almacen en memoria;
con una base real aquí vive el mapeo del ORM (por ejemplo SELECT ... FROM Reservas)."""
from datetime import datetime

from ..dominio.errores import NoEncontrado
from ..dominio.objetos_valor import EstadoReserva, EstadoSesion
from ..dominio.repositorios import (DisputaRepository, PagoRepository, ReservaRepository,
                                    SesionRepository, TutorRepository)
from .almacen import Almacen


class _SqlBase:
    def __init__(self, almacen: Almacen):
        self._a = almacen

    def _obtener(self, coleccion: dict, id: str):
        try:
            return coleccion[id]
        except KeyError:
            raise NoEncontrado(id) from None

    def _guardar(self, coleccion: dict, id: str, raiz) -> None:
        coleccion[id] = raiz
        self._a.pendientes.append(raiz)


class SqlReservaRepository(_SqlBase, ReservaRepository):
    def obtenerPorId(self, id): return self._obtener(self._a.reservas, id)
    def guardar(self, reserva): self._guardar(self._a.reservas, reserva.idReserva, reserva)
    def pendientesVencidas(self, ahora: datetime):
        return [r for r in self._a.reservas.values()
                if r.estado is EstadoReserva.PENDIENTE and r.plazo.estaVencido(ahora)]


class SqlSesionRepository(_SqlBase, SesionRepository):
    def obtenerPorId(self, id): return self._obtener(self._a.sesiones, id)
    def guardar(self, sesion): self._guardar(self._a.sesiones, sesion.idSesion, sesion)
    def obtenerSesionesConfirmadasPorTutor(self, tutorId):
        activas = (EstadoSesion.PROGRAMADA, EstadoSesion.EN_CURSO)
        return [s for s in self._a.sesiones.values() if s.tutorId == tutorId and s.estado in activas]


class SqlTutorRepository(_SqlBase, TutorRepository):
    def obtenerPorId(self, id): return self._obtener(self._a.tutores, id)
    def guardar(self, tutor): self._guardar(self._a.tutores, tutor.idTutor, tutor)


class SqlPagoRepository(_SqlBase, PagoRepository):
    def porReserva(self, reservaId):
        for p in self._a.pagos.values():
            if p.reservaId == reservaId:
                return p
        raise NoEncontrado(reservaId)
    def guardar(self, pago): self._guardar(self._a.pagos, pago.idPago, pago)


class SqlDisputaRepository(_SqlBase, DisputaRepository):
    def obtenerPorId(self, id): return self._obtener(self._a.disputas, id)
    def actualizar(self, disputa): self._guardar(self._a.disputas, disputa.idDisputa, disputa)
