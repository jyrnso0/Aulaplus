"""Servicios de dominio: reglas que no pertenecen a un solo aggregate."""
from .errores import HorarioNoDisponible
from .objetos_valor import Cancelacion, Dinero, Horario, Rol
from .sesion import Sesion


class ValidadorTraslapeHorario:
    """BR-0006: un tutor no puede tener dos sesiones confirmadas traslapadas."""

    def verificarTraslape(self, horario: Horario, sesiones: list[Sesion]) -> None:
        for sesion in sesiones:
            if horario.traslapaCon(sesion.horario):
                raise HorarioNoDisponible("El tutor ya tiene una sesión en ese horario (BR-0006)")


class PoliticaDeReembolso:
    """Cuánto se devuelve según el motivo y quién cancela (BR-0004, BR-0009).

    Esqueleto con dos causas. La propuesta SOLID-O es convertirla en una interfaz con una
    implementación por causa para no editar esta clase cuando aparezca una causa nueva.
    """

    def calcularMonto(self, motivo: str, cancelacion: Cancelacion, importe: Dinero) -> Dinero:
        if motivo == "ausencia_tutor":
            return importe  # BR-0009: reembolso del 100%
        if motivo == "cancelacion":
            if cancelacion.solicitante is Rol.ESTUDIANTE and cancelacion.esTardia:
                return importe.por("0.50")  # el estudiante pierde el 50% (BR-0004)
            return importe
        raise ValueError(f"Motivo sin política definida: {motivo}")
