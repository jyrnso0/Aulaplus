from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Frontera transaccional de un caso de uso: o se guarda todo, o no se guarda nada."""

    @abstractmethod
    def begin(self) -> None: ...
    @abstractmethod
    def commit(self) -> None: ...
    @abstractmethod
    def rollback(self) -> None: ...
