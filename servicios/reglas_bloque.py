from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from configuracion import JORNADAS
from servicios.calculo_horas import horas_tipo, minutos_programados


@dataclass(frozen=True)
class ContextoBloque:
    """Datos que una regla necesita para juzgar un bloque candidato."""
    asignacion: object
    candidato: object
    asignaciones: tuple
    original: object = None


class ReglaBloque(ABC):
    """Una regla de planificación. Para añadir una nueva, se crea otra subclase."""

    @abstractmethod
    def verificar(self, contexto: ContextoBloque) -> None:
        """Lanza ValueError si el bloque candidato no cumple la regla."""


class AulaRegistrada(ReglaBloque):
    def __init__(self, aulas):
        self._aulas = aulas

    def verificar(self, contexto):
        if not any(a is contexto.candidato.aula for a in self._aulas):
            raise ValueError("El aula no está registrada en el gestor.")


class DentroDeJornada(ReglaBloque):
    def verificar(self, contexto):
        paralelo = contexto.asignacion.paralelo
        ini_j, fin_j = JORNADAS[paralelo.jornada]
        c = contexto.candidato
        if c.hora_inicio < ini_j or c.hora_fin > fin_j:
            raise ValueError(
                f"El bloque queda fuera de la jornada {paralelo.jornada} "
                f"({ini_j:%H:%M}-{fin_j:%H:%M})."
            )


class CapacidadDelAula(ReglaBloque):
    def verificar(self, contexto):
        aula = contexto.candidato.aula
        cupo = contexto.asignacion.paralelo.cupo_maximo
        if aula.capacidad < cupo:
            raise ValueError(
                f"El aula {aula.codigo_aula} (capacidad {aula.capacidad}) no cubre "
                f"el cupo del paralelo ({cupo})."
            )


class TipoDeSesionAdmitido(ReglaBloque):
    def verificar(self, contexto):
        aula = contexto.candidato.aula
        tipo = contexto.candidato.tipo_sesion
        if not aula.admite(tipo):
            raise ValueError(f"El aula {aula.codigo_aula} no admite sesiones de {tipo}.")


class EquipamientoDelLaboratorio(ReglaBloque):
    def verificar(self, contexto):
        aula = contexto.candidato.aula
        if contexto.candidato.tipo_sesion == "PRACTICA" and not aula.verificar_equipamiento():
            raise ValueError(f"El laboratorio {aula.codigo_aula} no tiene equipamiento registrado.")


class DocenteDisponible(ReglaBloque):
    def verificar(self, contexto):
        c = contexto.candidato
        if not contexto.asignacion.docente.esta_disponible(c.dia, c.hora_inicio, c.hora_fin):
            raise ValueError("El docente no está disponible en ese intervalo.")


class SinCruces(ReglaBloque):
    def verificar(self, contexto):
        docente = contexto.asignacion.docente
        paralelo = contexto.asignacion.paralelo
        for otra in contexto.asignaciones:
            for h in otra.horarios:
                if h is contexto.original or not contexto.candidato.detectar_conflicto(h):
                    continue
                if otra.docente is docente:
                    raise ValueError("Cruce de horario: el docente ya tiene clase en ese intervalo.")
                if otra.paralelo is paralelo:
                    raise ValueError("Cruce de horario: el paralelo ya tiene clase en ese intervalo.")


class AulaLibre(ReglaBloque):
    def verificar(self, contexto):
        aula = contexto.candidato.aula
        if not aula.verificar_disponibilidad(contexto.candidato, ignorar=contexto.original):
            raise ValueError(f"El aula {aula.codigo_aula} está ocupada en ese intervalo.")


class HorasPermitidas(ReglaBloque):
    def verificar(self, contexto):
        c = contexto.candidato
        permitido = horas_tipo(contexto.asignacion.asignatura, c.tipo_sesion) * 60
        usado = minutos_programados(contexto.asignacion, c.tipo_sesion, excluir=contexto.original)
        if usado + c.calcular_duracion() > permitido:
            raise ValueError(
                f"Se superan las horas de {c.tipo_sesion}: "
                f"{usado} min programados + {c.calcular_duracion()} min > {permitido} min."
            )


def reglas_estandar(aulas) -> list[ReglaBloque]:
    """Reglas vigentes, en el orden en que se comprueban."""
    return [
        AulaRegistrada(aulas),
        DentroDeJornada(),
        CapacidadDelAula(),
        TipoDeSesionAdmitido(),
        EquipamientoDelLaboratorio(),
        DocenteDisponible(),
        SinCruces(),
        AulaLibre(),
        HorasPermitidas(),
    ]