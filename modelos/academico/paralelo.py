"""Modelo de paralelo académico."""

from .asignatura import Asignatura
from .nivel import Nivel
from .periodo_academico import PeriodoAcademico
from .validaciones import entero, texto_no_vacio
from configuracion import JORNADAS


class Paralelo:
    def __init__(self, codigo, jornada, cupo_maximo, nivel, periodo):
        texto_no_vacio(codigo, "El código")
        texto_no_vacio(jornada, "La jornada")
        jornada_normalizada = jornada.strip().upper()
        if jornada_normalizada not in JORNADAS:
            raise ValueError("La jornada debe ser MATUTINA, VESPERTINA o NOCTURNA")
        entero(cupo_maximo, "El cupo máximo", 1)
        if not isinstance(nivel, Nivel):
            raise ValueError("Se requiere un nivel válido")
        if not isinstance(periodo, PeriodoAcademico):
            raise ValueError("Se requiere un periodo académico válido")
        self.codigo = codigo.strip().upper()
        self.jornada = jornada_normalizada
        self.cupo_maximo = cupo_maximo
        self.nivel = nivel
        self.periodo = periodo
        self._estudiantes = []
        self._asignaciones = []

    @property
    def numero_estudiantes(self):
        return len(self._estudiantes)

    def verificar_cupo(self):
        return self.numero_estudiantes < self.cupo_maximo

    @staticmethod
    def _mismo_estudiante(registrado, estudiante):
        if registrado is estudiante:
            return True
        id_registrado = getattr(registrado, "id", None)
        id_estudiante = getattr(estudiante, "id", None)
        if id_registrado is not None and id_estudiante is not None:
            return id_registrado == id_estudiante
        return registrado == estudiante

    def agregar_estudiante(self, estudiante):
        if any(self._mismo_estudiante(e, estudiante) for e in self._estudiantes):
            raise ValueError("El estudiante ya está inscrito en este paralelo")
        if not self.verificar_cupo():
            raise ValueError("El paralelo no tiene cupos disponibles")
        self._estudiantes.append(estudiante)

    def quitar_estudiante(self, estudiante):
        for indice, inscrito in enumerate(self._estudiantes):
            if self._mismo_estudiante(inscrito, estudiante):
                del self._estudiantes[indice]
                return
        raise ValueError("El estudiante no está inscrito en este paralelo")

    def agregar_asignacion(self, asignacion):
        asignatura = getattr(asignacion, "asignatura", None)
        if getattr(asignacion, "paralelo", None) is not self:
            raise ValueError("La asignación debe pertenecer a este paralelo")
        if not isinstance(asignatura, Asignatura):
            raise ValueError("La asignación debe referirse a una asignatura")
        if not any(a is asignatura for a in self.nivel.obtener_asignaturas()):
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
