"""Modelo de paralelo académico."""

from .asignatura import Asignatura
from .nivel import Nivel
from .periodo_academico import PeriodoAcademico
from .validaciones import entero, texto_no_vacio


class Paralelo:
    def __init__(self, codigo, jornada, cupo_maximo, nivel, periodo):
        texto_no_vacio(codigo, "El código")
        texto_no_vacio(jornada, "La jornada")
        entero(cupo_maximo, "El cupo máximo", 1)
        if not isinstance(nivel, Nivel):
            raise ValueError("Se requiere un nivel válido")
        if not isinstance(periodo, PeriodoAcademico):
            raise ValueError("Se requiere un periodo académico válido")
        self.codigo = codigo.strip().upper()
        self.jornada = jornada.strip().upper()
        self.cupo_maximo = cupo_maximo
        self.nivel = nivel
        self.periodo = periodo
        self._estudiantes = []
        self._asignaciones = []
        nivel._paralelos.append(self)

    @property
    def numero_estudiantes(self):
        return len(self._estudiantes)

    def verificar_cupo(self):
        return self.numero_estudiantes < self.cupo_maximo

    def agregar_estudiante(self, estudiante):
        if any(e == estudiante for e in self._estudiantes):
            raise ValueError("El estudiante ya está inscrito en este paralelo")
        if not self.verificar_cupo():
            raise ValueError("El paralelo no tiene cupos disponibles")
        self._estudiantes.append(estudiante)

    def quitar_estudiante(self, estudiante):
        for indice, inscrito in enumerate(self._estudiantes):
            if inscrito == estudiante:
                del self._estudiantes[indice]
                return
        raise ValueError("El estudiante no está inscrito en este paralelo")

    def agregar_asignacion(self, asignacion):
        asignatura = getattr(asignacion, "asignatura", None)
        if getattr(asignacion, "paralelo", None) is not self:
            raise ValueError("La asignación debe pertenecer a este paralelo")
        if not isinstance(asignatura, Asignatura):
            raise ValueError("La asignación debe referirse a una asignatura")
        if not any(a.codigo.casefold() == asignatura.codigo.casefold()
                   for a in self.nivel._asignaturas):
            raise ValueError("La asignatura no pertenece al nivel del paralelo")
        if any(getattr(a, "asignatura", a).codigo.casefold() ==
               asignatura.codigo.casefold() for a in self._asignaciones):
            raise ValueError("La asignatura ya está asignada a este paralelo")
        self._asignaciones.append(asignacion)

    @property
    def asignaciones(self):
        return self._asignaciones.copy()

    @property
    def estudiantes(self):
        return self._estudiantes.copy()
