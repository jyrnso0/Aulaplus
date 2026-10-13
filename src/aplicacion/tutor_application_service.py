from ..dominio.repositorios import TutorRepository
from .dtos import ConfirmacionDTO
from .unit_of_work import UnitOfWork


class TutorApplicationService:
    def __init__(self, tutores: TutorRepository, uow: UnitOfWork):
        self._tutores, self._uow = tutores, uow

    def registrarDisponibilidad(self, idTutor: str, materia: str, franjaHoraria, modalidad: str) -> ConfirmacionDTO:
        """CU-02a: carga el Tutor, actualiza su disponibilidad por materia y persiste."""
        self._uow.begin()
        try:
            tutor = self._tutores.obtenerPorId(idTutor)
            franjas = list(tutor.disponibilidad[materia].franjas) if materia in tutor.disponibilidad else []
            franjas.append((franjaHoraria, modalidad))
            tutor.definirDisponibilidad(materia, franjas)
            self._tutores.guardar(tutor)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
        return ConfirmacionDTO(idTutor, materia)
