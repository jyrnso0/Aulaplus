"""Almacén en memoria que hace de «base de datos» del esqueleto. En producción lo reemplaza un ORM."""
from copy import deepcopy


class Almacen:
    def __init__(self):
        self.reservas: dict = {}
        self.sesiones: dict = {}
        self.tutores: dict = {}
        self.pagos: dict = {}
        self.disputas: dict = {}
        self.outbox: list = []        # eventos ya confirmados (después del commit)
        self.pendientes: list = []    # raíces guardadas en la transacción en curso
        self._snapshot = None

    _colecciones = ("reservas", "sesiones", "tutores", "pagos", "disputas")

    def tomarSnapshot(self):
        self._snapshot = {n: deepcopy(getattr(self, n)) for n in self._colecciones}
        self.pendientes = []

    def restaurar(self):
        if self._snapshot is not None:
            for n, datos in self._snapshot.items():
                setattr(self, n, datos)
        self._snapshot, self.pendientes = None, []

    def confirmar(self):
        for raiz in self.pendientes:
            self.outbox.extend(raiz.extraerEventos())  # los eventos salen solo después del commit
        self._snapshot, self.pendientes = None, []
