"""Contratos pequeños: cada cliente depende solo de las operaciones que usa."""
from __future__ import annotations

from abc import ABC, abstractmethod


class VerificadorBloques(ABC):
    """Lo que necesita quien solo quiere saber si un bloque es válido
    (el gestor y, más adelante, el generador automático)."""

    @abstractmethod
    def validar(self, asignacion, candidato, asignaciones, original=None) -> None:
        """Lanza ValueError si el bloque no cumple las reglas."""


class EditorPlanificacion(ABC):
    """Lo que necesita quien modifica la planificación (menú de la consola)."""

    @abstractmethod
    def crear_asignacion(self, id_asignacion, docente, asignatura, paralelo): ...

    @abstractmethod
    def crear_horario(self, id_horario, asignacion, dia, inicio, fin, aula, tipo_sesion): ...

    @abstractmethod
    def modificar_horario(self, asignacion, horario, dia, inicio, fin, aula, tipo_sesion) -> None: ...

    @abstractmethod
    def eliminar_horario(self, asignacion, horario) -> None: ...


class AuditorPlanificacion(ABC):
    """Lo que necesita quien solo revisa el estado (reportes, exportación,
    verificación del resultado del generador)."""

    @abstractmethod
    def validar_planificacion(self) -> list[str]:
        """Devuelve la lista de problemas encontrados (vacía si está completa)."""