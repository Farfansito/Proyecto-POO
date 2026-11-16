from __future__ import annotations

from modelos.horarios.horario import Horario


class AsignacionAcademica:
    def __init__(self, id_asignacion, docente, asignatura, paralelo):
        if isinstance(id_asignacion, bool) or not isinstance(id_asignacion, int) or id_asignacion <= 0:
            raise ValueError("id_asignacion debe ser un entero positivo.")
        if docente is None or asignatura is None or paralelo is None:
            raise ValueError("La asignación necesita docente, asignatura y paralelo.")
        self.id_asignacion = id_asignacion
        self.docente = docente
        self.asignatura = asignatura
        self.paralelo = paralelo
        self._horarios: list[Horario] = []

    @property
    def horas_semanales(self) -> int:
        return self.asignatura.horas_teoricas + self.asignatura.horas_practicas

    @property
    def horarios(self) -> list[Horario]:
        return list(self._horarios)

    def agregar_horario(self, horario: Horario) -> None:
        if not isinstance(horario, Horario):
            raise ValueError("Solo se pueden agregar objetos Horario.")
        if any(h is horario or h.id_horario == horario.id_horario for h in self._horarios):
            raise ValueError(f"El bloque {horario.id_horario} ya pertenece a la asignación.")
        self._horarios.append(horario)

    def quitar_horario(self, horario: Horario) -> None:
        for i, h in enumerate(self._horarios):
            if h is horario:
                del self._horarios[i]
                return
        raise ValueError("El bloque no pertenece a esta asignación.")