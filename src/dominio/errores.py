"""Errores de negocio. El campo `codigo` coincide con los errores tipados de la Etapa 4."""


class ErrorDeNegocio(Exception):
    codigo = "ERROR_DE_NEGOCIO"

    def __init__(self, mensaje: str = ""):
        super().__init__(mensaje or self.codigo)


class NoEncontrado(ErrorDeNegocio):
    codigo = "NO_ENCONTRADO"


class PlazoVencido(ErrorDeNegocio):
    codigo = "PLAZO_VENCIDO"  # BR-0001, BR-0007


class EstadoInvalido(ErrorDeNegocio):
    codigo = "ESTADO_INVALIDO"


class HorarioNoDisponible(ErrorDeNegocio):
    codigo = "HORARIO_NO_DISPONIBLE"  # BR-0006


class EvidenciaRequerida(ErrorDeNegocio):
    codigo = "EVIDENCIA_REQUERIDA"  # BR-0020
