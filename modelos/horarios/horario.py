"""Bloque semanal de clase (Horario). Autor: Richard Soledispa."""
from __future__ import annotations

import unicodedata
from datetime import time

from configuracion import DIAS, TIPOS_SESION

_METODOS_AULA = (
    "codigo_aula",
    "capacidad",
    "admite",
    "reservar",
    "liberar",
    "verificar_disponibilidad",
)


def normalizar_dia(dia) -> str:
    """Devuelve el día en mayúsculas y sin tildes (ej. 'miércoles' -> 'MIERCOLES')."""
    if not isinstance(dia, str):
        raise ValueError("El día debe ser texto.")
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", dia) if unicodedata.category(c) != "Mn"
    )
    return sin_tildes.strip().upper()


def _validar_hora(valor, nombre: str) -> None:
    if not isinstance(valor, time):
        raise ValueError(f"{nombre} debe ser un datetime.time.")
    if valor.second != 0 or valor.microsecond != 0:
        raise ValueError(f"{nombre} debe tener precisión de minutos (segundos en cero).")


def _minutos(hora: time) -> int:
    return hora.hour * 60 + hora.minute


def validar_datos_bloque(dia, hora_inicio, hora_fin, aula, tipo_sesion):
    """Valida los datos de un bloque y devuelve (dia, tipo_sesion) normalizados."""
    dia = normalizar_dia(dia)
    if dia not in DIAS:
        raise ValueError(f"Día inválido '{dia}'. Permitidos: {', '.join(DIAS)}.")
    _validar_hora(hora_inicio, "hora_inicio")
    _validar_hora(hora_fin, "hora_fin")
    if not hora_inicio < hora_fin:
        raise ValueError("La hora de inicio debe ser menor que la hora de fin.")
    if aula is None or not all(hasattr(aula, m) for m in _METODOS_AULA):
        raise ValueError("El bloque necesita un aula concreta registrada.")
    if not isinstance(tipo_sesion, str):
        raise ValueError("El tipo de sesión debe ser texto.")
    tipo_sesion = tipo_sesion.strip().upper()
    if tipo_sesion not in TIPOS_SESION:
        raise ValueError(
            f"Tipo de sesión inválido '{tipo_sesion}'. Permitidos: {', '.join(TIPOS_SESION)}."
        )
    return dia, tipo_sesion


class Horario:
    """Bloque semanal recurrente: día, intervalo, aula y tipo de sesión."""

    def __init__(self, id_horario, dia, hora_inicio, hora_fin, aula, tipo_sesion):
        if isinstance(id_horario, bool) or not isinstance(id_horario, int) or id_horario <= 0:
            raise ValueError("id_horario debe ser un entero positivo.")
        dia, tipo_sesion = validar_datos_bloque(dia, hora_inicio, hora_fin, aula, tipo_sesion)
        self.id_horario = id_horario
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.aula = aula
        self.tipo_sesion = tipo_sesion

    def calcular_duracion(self) -> int:
        """Duración real del bloque en minutos."""
        return _minutos(self.hora_fin) - _minutos(self.hora_inicio)

    def detectar_conflicto(self, otro: "Horario") -> bool:
        """True si ambos bloques se superponen en el tiempo (mismo día).

        Solo revisa el tiempo; el gestor decide si comparten aula/docente/paralelo.
        """
        if not isinstance(otro, Horario):
            raise ValueError("Solo se puede comparar con otro Horario.")
        return (
            self.dia == otro.dia
            and self.hora_inicio < otro.hora_fin
            and otro.hora_inicio < self.hora_fin
        )

    def datos(self) -> tuple:
        """Copia de los valores modificables (para restaurar si algo falla)."""
        return (self.dia, self.hora_inicio, self.hora_fin, self.aula, self.tipo_sesion)

    def aplicar_cambios(self, dia, hora_inicio, hora_fin, aula, tipo_sesion) -> None:
        """Uso interno del GestorHorarios. Valida todo y luego cambia los atributos.

        No toca reservas de aula: eso lo hace el gestor.
        """
        dia, tipo_sesion = validar_datos_bloque(dia, hora_inicio, hora_fin, aula, tipo_sesion)
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.aula = aula
        self.tipo_sesion = tipo_sesion

    def __repr__(self) -> str:
        codigo = getattr(self.aula, "codigo_aula", "?")
        return (
            f"Horario({self.id_horario}, {self.dia} "
            f"{self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}, {codigo}, {self.tipo_sesion})"
        )