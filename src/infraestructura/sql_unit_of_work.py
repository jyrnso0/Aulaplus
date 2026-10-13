from ..aplicacion.unit_of_work import UnitOfWork
from .almacen import Almacen


class SqlUnitOfWork(UnitOfWork):
    """Esqueleto: begin toma un snapshot, rollback lo restaura y commit publica los eventos al outbox.
    Con una base real, begin/commit/rollback serían los de la transacción del ORM."""

    def __init__(self, almacen: Almacen):
        self._almacen = almacen

    def begin(self) -> None:
        self._almacen.tomarSnapshot()

    def commit(self) -> None:
        self._almacen.confirmar()

    def rollback(self) -> None:
        self._almacen.restaurar()
