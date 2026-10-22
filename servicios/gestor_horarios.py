"""Gestor de horarios: todas las reglas de creación/modificación de bloques.

Autor: Richard Soledispa.
Regla de oro: una operación inválida deja el estado exactamente como estaba.
"""
from __future__ import annotations

from configuracion import JORNADAS
from modelos.academico.asignacion_academica import AsignacionAcademica
from modelos.horarios.horario import Horario


class GestorHorarios:
    def __init__(self, periodo, aulas):
        if periodo is None:
            raise ValueError("El gestor necesita un periodo académico.")
        self.periodo = periodo
        if isinstance(aulas, dict):
            aulas = aulas.values()
        self._aulas = list(aulas)

    @property
    def aulas(self) -> list:
        return list(self._aulas)

    # ------------------------------------------------------------ consultas
    def _asignaciones(self) -> list[AsignacionAcademica]:
        """Todas las asignaciones del periodo (salen de los paralelos)."""
        return [a for p in self.periodo.paralelos for a in p.asignaciones]

    def _exigir_periodo_abierto(self) -> None:
        if self.periodo.estado != "ABIERTO":
            raise ValueError("El periodo no está ABIERTO: no se permiten modificaciones.")

    def _exigir_asignacion_del_periodo(self, asignacion) -> None:
        if not any(a is asignacion for a in self._asignaciones()):
            raise ValueError("La asignación no pertenece a este periodo.")

    @staticmethod
    def _horas_tipo(asignatura, tipo: str) -> int:
        return asignatura.horas_teoricas if tipo == "TEORIA" else asignatura.horas_practicas

    @staticmethod
    def _minutos_programados(asignacion, tipo: str, excluir=None) -> int:
        return sum(
            h.calcular_duracion()
            for h in asignacion.horarios
            if h.tipo_sesion == tipo and h is not excluir
        )

    # ---------------------------------------------------------- asignaciones
    def crear_asignacion(self, id_asignacion, docente, asignatura, paralelo) -> AsignacionAcademica:
        self._exigir_periodo_abierto()
        if not any(p is paralelo for p in self.periodo.paralelos):
            raise ValueError("El paralelo no está registrado en este periodo.")
        if not any(a.codigo == asignatura.codigo for a in paralelo.nivel.obtener_asignaturas()):
            raise ValueError("La asignatura no pertenece al nivel del paralelo.")
        if any(a.id_asignacion == id_asignacion for a in self._asignaciones()):
            raise ValueError(f"Ya existe una asignación con ID {id_asignacion}.")
        if any(a.asignatura.codigo == asignatura.codigo for a in paralelo.asignaciones):
            raise ValueError("La asignatura ya está asignada a ese paralelo.")

        asignacion = AsignacionAcademica(id_asignacion, docente, asignatura, paralelo)
        carga = docente.horas_asignadas(self.periodo) + asignacion.horas_semanales
        if carga > docente.max_horas_semanales:
            raise ValueError(
                f"El docente superaría su máximo semanal ({carga} > {docente.max_horas_semanales} horas)."
            )

        docente.asignar_asignatura(asignacion)
        try:
            paralelo.agregar_asignacion(asignacion)
        except Exception:
            docente.quitar_asignacion(asignacion)  # revertir la primera escritura
            raise
        return asignacion

    # --------------------------------------------------------------- bloques
    def _validar_bloque(self, asignacion, candidato: Horario, original=None) -> None:
        """Valida un bloque candidato en el orden de la guía. No modifica nada."""
        self._exigir_periodo_abierto()                                   # 1
        self._exigir_asignacion_del_periodo(asignacion)
        aula = candidato.aula
        if not any(a is aula for a in self._aulas):
            raise ValueError("El aula no está registrada en el gestor.")

        paralelo = asignacion.paralelo                                    # 3
        ini_j, fin_j = JORNADAS[paralelo.jornada]
        if candidato.hora_inicio < ini_j or candidato.hora_fin > fin_j:
            raise ValueError(
                f"El bloque queda fuera de la jornada {paralelo.jornada} "
                f"({ini_j:%H:%M}-{fin_j:%H:%M})."
            )

        if aula.capacidad < paralelo.cupo_maximo:                         # 4
            raise ValueError(
                f"El aula {aula.codigo_aula} (capacidad {aula.capacidad}) no cubre "
                f"el cupo del paralelo ({paralelo.cupo_maximo})."
            )
        if not aula.admite(candidato.tipo_sesion):
            raise ValueError(f"El aula {aula.codigo_aula} no admite sesiones de {candidato.tipo_sesion}.")
        if candidato.tipo_sesion == "PRACTICA" and hasattr(aula, "verificar_equipamiento"):
            if not aula.verificar_equipamiento():
                raise ValueError(f"El laboratorio {aula.codigo_aula} no tiene equipamiento registrado.")

        docente = asignacion.docente                                      # 5
        if not docente.esta_disponible(candidato.dia, candidato.hora_inicio, candidato.hora_fin):
            raise ValueError("El docente no está disponible en ese intervalo.")

        for otra in self._asignaciones():                                 # 6
            for h in otra.horarios:
                if h is original or not candidato.detectar_conflicto(h):
                    continue
                if otra.docente is docente:
                    raise ValueError("Cruce de horario: el docente ya tiene clase en ese intervalo.")
                if otra.paralelo is paralelo:
                    raise ValueError("Cruce de horario: el paralelo ya tiene clase en ese intervalo.")

        if not aula.verificar_disponibilidad(candidato, ignorar=original):  # 7
            raise ValueError(f"El aula {aula.codigo_aula} está ocupada en ese intervalo.")

        permitido = self._horas_tipo(asignacion.asignatura, candidato.tipo_sesion) * 60  # 8
        usado = self._minutos_programados(asignacion, candidato.tipo_sesion, excluir=original)
        if usado + candidato.calcular_duracion() > permitido:
            raise ValueError(
                f"Se superan las horas de {candidato.tipo_sesion}: "
                f"{usado} min programados + {candidato.calcular_duracion()} min > {permitido} min."
            )

    def crear_horario(self, id_horario, asignacion, dia, inicio, fin, aula, tipo_sesion) -> Horario:
        candidato = Horario(id_horario, dia, inicio, fin, aula, tipo_sesion)  # 2
        self._exigir_periodo_abierto()
        if any(h.id_horario == id_horario for a in self._asignaciones() for h in a.horarios):
            raise ValueError(f"Ya existe un bloque con ID {id_horario} en el periodo.")
        self._validar_bloque(asignacion, candidato)

        aula.reservar(candidato)                                          # 9
        try:
            asignacion.agregar_horario(candidato)
        except Exception:
            aula.liberar(candidato)
            raise
        return candidato

    def modificar_horario(self, asignacion, horario, dia, inicio, fin, aula, tipo_sesion) -> None:
        self._exigir_periodo_abierto()
        self._exigir_asignacion_del_periodo(asignacion)
        if not any(h is horario for h in asignacion.horarios):
            raise ValueError("El bloque no pertenece a la asignación.")
        candidato = Horario(horario.id_horario, dia, inicio, fin, aula, tipo_sesion)
        self._validar_bloque(asignacion, candidato, original=horario)

        anterior = horario.datos()
        aula_anterior = horario.aula
        aula_anterior.liberar(horario)          # si falla, aún no se cambió nada
        try:
            horario.aplicar_cambios(candidato.dia, inicio, fin, aula, candidato.tipo_sesion)
            aula.reservar(horario)
        except Exception:
            horario.aplicar_cambios(*anterior)  # restaurar atributos y reserva
            aula_anterior.reservar(horario)
            raise

    def eliminar_horario(self, asignacion, horario) -> None:
        self._exigir_periodo_abierto()
        self._exigir_asignacion_del_periodo(asignacion)
        if not any(h is horario for h in asignacion.horarios):
            raise ValueError("El bloque no pertenece a la asignación.")
        horario.aula.liberar(horario)
        try:
            asignacion.quitar_horario(horario)
        except Exception:
            horario.aula.reservar(horario)
            raise

    # ----------------------------------------------------------- validación
    def validar_planificacion(self) -> list[str]:
        """Lista de problemas. [] significa periodo completo y válido."""
        problemas: list[str] = []
        paralelos = self.periodo.paralelos
        if not paralelos:
            return ["El periodo no tiene paralelos: planificación incompleta."]

        for p in paralelos:
            if not p.asignaciones:
                problemas.append(f"El paralelo {p.codigo} no tiene asignaciones.")
                continue
            asignadas = {a.asignatura.codigo for a in p.asignaciones}
            for materia in p.nivel.obtener_asignaturas():
                if materia.codigo not in asignadas:
                    problemas.append(
                        f"Paralelo {p.codigo}: la asignatura {materia.codigo} no tiene docente asignado."
                    )
            for a in p.asignaciones:
                for tipo in ("TEORIA", "PRACTICA"):
                    requerido = self._horas_tipo(a.asignatura, tipo) * 60
                    programado = self._minutos_programados(a, tipo)
                    if programado < requerido:
                        problemas.append(
                            f"Paralelo {p.codigo} · {a.asignatura.codigo}: faltan "
                            f"{requerido - programado} min de {tipo} "
                            f"({programado} de {requerido} programados)."
                        )
                    elif programado > requerido:
                        problemas.append(
                            f"Paralelo {p.codigo} · {a.asignatura.codigo}: sobran "
                            f"{programado - requerido} min de {tipo}."
                        )
        return problemas