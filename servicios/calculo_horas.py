"""Cálculo de horas requeridas y programadas por asignación.

Lo usan tanto el validador de bloques como la validación global de la
planificación, por eso vive aparte del gestor.
"""
from __future__ import annotations


def horas_tipo(asignatura, tipo: str) -> int:
    return asignatura.horas_teoricas if tipo == "TEORIA" else asignatura.horas_practicas


def minutos_programados(asignacion, tipo: str, excluir=None) -> int:
    return sum(
        h.calcular_duracion()
        for h in asignacion.horarios
        if h.tipo_sesion == tipo and h is not excluir
    )