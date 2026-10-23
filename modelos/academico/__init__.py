"""Catálogo académico del sistema SCHOS."""

from .asignatura import Asignatura
from .nivel import Nivel
from .paralelo import Paralelo
from .periodo_academico import PeriodoAcademico

__all__ = ["Asignatura", "Nivel", "Paralelo", "PeriodoAcademico"]
