from __future__ import annotations

from configuracion import JORNADAS
from servicios.calculo_horas import horas_tipo, minutos_programados


class ValidadorBloques:
    """Decide si un bloque candidato cumple las reglas de planificación.

    Solo comprueba: no reserva aulas ni agrega horarios. Por eso el
    generador automático podrá reutilizarlo para probar opciones.
    """

    def __init__(self, aulas):
        self._aulas = aulas

    def validar(self, asignacion, candidato, asignaciones, original=None) -> None:
        aula = candidato.aula
        if not any(a is aula for a in self._aulas):
            raise ValueError("El aula no está registrada en el gestor.")

        paralelo = asignacion.paralelo
        ini_j, fin_j = JORNADAS[paralelo.jornada]
        if candidato.hora_inicio < ini_j or candidato.hora_fin > fin_j:
            raise ValueError(
                f"El bloque queda fuera de la jornada {paralelo.jornada} "
                f"({ini_j:%H:%M}-{fin_j:%H:%M})."
            )

        if aula.capacidad < paralelo.cupo_maximo:
            raise ValueError(
                f"El aula {aula.codigo_aula} (capacidad {aula.capacidad}) no cubre "
                f"el cupo del paralelo ({paralelo.cupo_maximo})."
            )
        if not aula.admite(candidato.tipo_sesion):
            raise ValueError(f"El aula {aula.codigo_aula} no admite sesiones de {candidato.tipo_sesion}.")
        if candidato.tipo_sesion == "PRACTICA" and hasattr(aula, "verificar_equipamiento"):
            if not aula.verificar_equipamiento():
                raise ValueError(f"El laboratorio {aula.codigo_aula} no tiene equipamiento registrado.")

        docente = asignacion.docente
        if not docente.esta_disponible(candidato.dia, candidato.hora_inicio, candidato.hora_fin):
            raise ValueError("El docente no está disponible en ese intervalo.")

        for otra in asignaciones:
            for h in otra.horarios:
                if h is original or not candidato.detectar_conflicto(h):
                    continue
                if otra.docente is docente:
                    raise ValueError("Cruce de horario: el docente ya tiene clase en ese intervalo.")
                if otra.paralelo is paralelo:
                    raise ValueError("Cruce de horario: el paralelo ya tiene clase en ese intervalo.")

        if not aula.verificar_disponibilidad(candidato, ignorar=original):
            raise ValueError(f"El aula {aula.codigo_aula} está ocupada en ese intervalo.")

        permitido = horas_tipo(asignacion.asignatura, candidato.tipo_sesion) * 60
        usado = minutos_programados(asignacion, candidato.tipo_sesion, excluir=original)
        if usado + candidato.calcular_duracion() > permitido:
            raise ValueError(
                f"Se superan las horas de {candidato.tipo_sesion}: "
                f"{usado} min programados + {candidato.calcular_duracion()} min > {permitido} min."
            )