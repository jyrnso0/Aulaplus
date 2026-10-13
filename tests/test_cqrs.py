"""CQRS: las Queries leen de un read model y su DTO no expone datos internos del Tutor."""
from dataclasses import fields
from datetime import date

from aulaplus.aplicacion.consultas import (ConsultarPerfilTutorQuery, ConsultarPerfilTutorQueryHandler,
                                           PerfilTutorReadModel, PerfilTutorViewDTO)


class PerfilFalso(PerfilTutorReadModel):
    def perfil(self, idTutor):
        return PerfilTutorViewDTO(idTutor, "Ana", ["Cálculo"], ["en línea"], 4.8, 25, [])


def test_perfil_publico_no_expone_ausencias_ni_estado_de_cuenta():
    dto = ConsultarPerfilTutorQueryHandler(PerfilFalso()).handle(ConsultarPerfilTutorQuery("t1"))
    assert dto.calificacionPromedio == 4.8
    campos = {f.name for f in fields(PerfilTutorViewDTO)}
    assert not campos & {"historialAusencias", "estadoCuenta", "datosPago"}
