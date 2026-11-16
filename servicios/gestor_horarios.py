from __future__ import annotations

from modelos.academico.asignacion_academica import AsignacionAcademica
from modelos.horarios.horario import Horario
from servicios.calculo_horas import horas_tipo, minutos_programados
from servicios.reglas_bloque import reglas_estandar
from servicios.validador_bloques import ValidadorBloques


class GestorHorarios:
    def __init__(self, periodo, aulas):
        if periodo is None:
            raise ValueError("El gestor necesita un periodo académico.")
        self.periodo = periodo
        if isinstance(aulas, dict):
            aulas = aulas.values()
        self._aulas = list(aulas)
        self._validador = ValidadorBloques(reglas_estandar(self._aulas))

    @property
    def aulas(self) -> list:
        return list(self._aulas)

    def _paralelos(self) -> list:
        paralelos = self.periodo.paralelos
        return list(paralelos() if callable(paralelos) else paralelos)

    def _asignaciones(self) -> list[AsignacionAcademica]:
        return [a for p in self._paralelos() for a in p.asignaciones]

    def _exigir_periodo_abierto(self) -> None:
        if self.periodo.estado != "ABIERTO":
            raise ValueError("El periodo no está ABIERTO: no se permiten modificaciones.")

    def _exigir_asignacion_del_periodo(self, asignacion) -> None:
        if not any(a is asignacion for a in self._asignaciones()):
            raise ValueError("La asignación no pertenece a este periodo.")

    def crear_asignacion(self, id_asignacion, docente, asignatura, paralelo) -> AsignacionAcademica:
        self._exigir_periodo_abierto()
        if not any(p is paralelo for p in self._paralelos()):
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
            docente.quitar_asignacion(asignacion)
            raise
        return asignacion

    def _validar_bloque(self, asignacion, candidato: Horario, original=None) -> None:
        self._exigir_periodo_abierto()
        self._exigir_asignacion_del_periodo(asignacion)
        self._validador.validar(asignacion, candidato, self._asignaciones(), original)

    def crear_horario(self, id_horario, asignacion, dia, inicio, fin, aula, tipo_sesion) -> Horario:
        candidato = Horario(id_horario, dia, inicio, fin, aula, tipo_sesion)
        self._exigir_periodo_abierto()
        if any(h.id_horario == id_horario for a in self._asignaciones() for h in a.horarios):
            raise ValueError(f"Ya existe un bloque con ID {id_horario} en el periodo.")
        self._validar_bloque(asignacion, candidato)

        aula.reservar(candidato)
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
        aula_anterior.liberar(horario)
        try:
            horario.aplicar_cambios(candidato.dia, inicio, fin, aula, candidato.tipo_sesion)
            aula.reservar(horario)
        except Exception:
            horario.aplicar_cambios(*anterior)
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

    def validar_planificacion(self) -> list[str]:
        problemas: list[str] = []
        paralelos = self._paralelos()
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
                    requerido = horas_tipo(a.asignatura, tipo) * 60
                    programado = minutos_programados(a, tipo)
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