from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modelos.horarios.horario import Horario


class Aula(ABC):
    """Clase abstracta: AulaTeorica, Laboratorio, Auditorio, SalaSustentacion.

    Aula controla su propia ocupación (reservas). El aforo del paralelo y la
    modificación completa de un bloque reservado pertenecen al gestor.
    """

    def __init__(self, codigo_aula: str, capacidad: int, piso: int, tiene_proyector: bool):
        self.codigo_aula = self._validar_codigo(codigo_aula)
        self.capacidad = self._validar_capacidad(capacidad)
        self.piso = self._validar_piso(piso)
        self.tiene_proyector = self._validar_bool(tiene_proyector, "tiene_proyector")
        self._reservas: list[Horario] = []

  
    @staticmethod
    def _validar_codigo(codigo) -> str:
        if not isinstance(codigo, str):
            raise TypeError("codigo_aula debe ser una cadena")
        if not codigo.strip():
            raise ValueError("codigo_aula no puede estar vacío")
        return codigo

    @staticmethod
    def _validar_capacidad(capacidad) -> int:
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise TypeError("capacidad debe ser un entero")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser positiva")
        return capacidad

    @staticmethod
    def _validar_piso(piso) -> int:
        if isinstance(piso, bool) or not isinstance(piso, int):
            raise TypeError("piso debe ser un entero")
        if piso < 0:
            raise ValueError("piso no puede ser negativo")
        return piso

    @staticmethod
    def _validar_bool(valor, nombre: str) -> bool:
        if not isinstance(valor, bool):
            raise TypeError(f"{nombre} debe ser booleano")
        return valor


    @abstractmethod
    def tipo(self) -> str:
        """TEORICA, LABORATORIO, AUDITORIO o SUSTENTACION."""

    def admite(self, tipo_sesion: str) -> bool:
        """TEORIA solo para AulaTeorica; PRACTICA solo para Laboratorio."""
        return False

    def verificar_disponibilidad(self, horario: Horario, ignorar: Horario | None = None) -> bool:
        """True si no se cruza con ninguna reserva (misma día y horas solapadas).

        Omite únicamente el objeto `ignorar` (identidad), de modo que una
        modificación se valida sin quitar la reserva anterior.
        """
        return not any(r is not ignorar and r.detectar_conflicto(horario)
                       for r in self._reservas)

    def reservar(self, horario: Horario) -> None:
        if horario.aula is not self:
            raise ValueError("el horario no pertenece a esta aula (horario.aula is not self)")
        if any(r is horario for r in self._reservas):
            raise ValueError("el horario ya está reservado en esta aula")
        if not self.verificar_disponibilidad(horario):
            raise ValueError(f"el aula {self.codigo_aula} está ocupada en {horario}")
        self._reservas.append(horario)

    def liberar(self, horario: Horario) -> None:
        for i, r in enumerate(self._reservas):
            if r is horario:
                del self._reservas[i]
                return
        raise ValueError("el horario no está reservado en esta aula")

    @property
    def reservas(self) -> list[Horario]:
        return list(self._reservas)

    def __str__(self) -> str:
        return f"{self.tipo()}[{self.codigo_aula}]"
