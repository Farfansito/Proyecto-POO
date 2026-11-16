"""Patrón estructural Facade aplicado al flujo de matrícula de SCHOS.

La consola (o cualquier otro cliente) solo habla con ``FachadaMatricula``.
La fachada coordina Estudiante, Matricula, Paralelo y PeriodoAcademico, y
garantiza que si una operación falla no quede un estado parcial.

Ejecución del ejemplo de uso (desde la carpeta raíz del proyecto):
    python -m servicios.fachada_matricula
"""
from __future__ import annotations

from modelos.academico.matricula import Matricula
from modelos.academico.paralelo import Paralelo
from modelos.usuarios.estudiante import Estudiante


class FachadaMatricula:
    """Punto de entrada único para solicitar, confirmar y consultar matrículas."""

    def __init__(self, sistema):
        self._sistema = sistema

    def solicitar_matricula(self, id_estudiante: int) -> Matricula:
        """Crea una matrícula PENDIENTE para el estudiante en el periodo actual."""
        estudiante = self._buscar_estudiante(id_estudiante)
        return estudiante.solicitar_matricula(
            self._periodo_actual(), self._sistema.nuevo_id("matricula")
        )

    def confirmar_matricula(self, id_estudiante: int, codigo_paralelo: str) -> Matricula:
        """Elige el paralelo y confirma la matrícula PENDIENTE existente.

        Si algo falla, la matrícula vuelve exactamente al estado anterior
        (sigue PENDIENTE, con el mismo paralelo que tenía antes).
        """
        estudiante = self._buscar_estudiante(id_estudiante)
        paralelo = self._buscar_paralelo(codigo_paralelo)
        pendiente = self._matricula_pendiente(estudiante, paralelo)
        if pendiente is None:
            raise ValueError("No hay una matrícula pendiente en ese periodo.")
        return self._elegir_y_confirmar(estudiante, pendiente, paralelo)

    def matricular(self, id_estudiante: int, codigo_paralelo: str) -> Matricula:
        """Operación completa: solicitar (si hace falta) + elegir + confirmar.

        Es atómica: si cualquier paso falla se deshace lo que esta misma
        llamada haya hecho, y el estudiante queda como estaba antes.
        """
        estudiante = self._buscar_estudiante(id_estudiante)
        paralelo = self._buscar_paralelo(codigo_paralelo)

        pendiente = self._matricula_pendiente(estudiante, paralelo)
        creada_aqui = pendiente is None
        if creada_aqui:
            pendiente = estudiante.solicitar_matricula(
                self._periodo_actual(), self._sistema.nuevo_id("matricula")
            )
        try:
            return self._elegir_y_confirmar(estudiante, pendiente, paralelo)
        except ValueError:
            if creada_aqui:
                pendiente.cancelar()
            raise

    def consultar_horario(self, id_estudiante: int) -> list:
        """Horarios del estudiante (solo cuenta la matrícula CONFIRMADA)."""
        estudiante = self._buscar_estudiante(id_estudiante)
        return estudiante.ver_horario(self._periodo_actual())

    def _periodo_actual(self):
        if self._sistema.periodo is None:
            raise ValueError("Primero debes crear un periodo.")
        return self._sistema.periodo

    def _buscar_estudiante(self, id_estudiante) -> Estudiante:
        usuario = self._sistema.usuarios.get(id_estudiante)
        if not isinstance(usuario, Estudiante):
            raise ValueError("No existe un estudiante con ese ID.")
        return usuario

    def _buscar_paralelo(self, codigo) -> Paralelo:
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("Debes indicar el código del paralelo.")
        buscado = codigo.strip().upper()
        for paralelo in self._periodo_actual().paralelos:
            if paralelo.codigo == buscado:
                return paralelo
        raise ValueError("No existe ese paralelo.")

    @staticmethod
    def _matricula_pendiente(estudiante: Estudiante, paralelo: Paralelo):
        for matricula in estudiante.matriculas:
            if matricula.periodo is paralelo.periodo and matricula.estado == "PENDIENTE":
                return matricula
        return None

    @staticmethod
    def _elegir_y_confirmar(estudiante, matricula, paralelo) -> Matricula:
        paralelo_anterior = matricula.paralelo
        try:
            estudiante.matricular(paralelo)   
            matricula.confirmar()             
        except ValueError:
            if matricula.estado == "PENDIENTE":
                matricula.paralelo = paralelo_anterior
            raise
        return matricula

if __name__ == "__main__":
    from datetime import date, time

    from aplicacion import SistemaSCHOS
    from modelos.academico.asignatura import Asignatura
    from modelos.academico.nivel import Nivel
    from modelos.academico.periodo_academico import PeriodoAcademico
    from modelos.aulas.aula_teorica import AulaTeorica
    from modelos.usuarios.docente import Docente
    from servicios.gestor_horarios import GestorHorarios

    sistema = SistemaSCHOS()
    periodo = PeriodoAcademico("2026-2", "Periodo 2026-2", date(2026, 11, 1), date(2027, 3, 31))
    periodo.abrir_periodo()
    sistema.establecer_periodo(periodo)

    nivel = Nivel(1, "Primer nivel")
    poo = Asignatura("POO-101", "Programación Orientada a Objetos", 4, 3, 1)
    nivel.agregar_asignatura(poo)

    pa = Paralelo("A", "MATUTINA", 1, nivel, periodo)   
    pb = Paralelo("B", "VESPERTINA", 30, nivel, periodo)
    periodo.agregar_paralelo(pa)
    periodo.agregar_paralelo(pb)

    aula = AulaTeorica("A-101", 40, 1, True)
    sistema.registrar_aula(aula)
    docente = Docente(sistema.nuevo_id("usuario"), "Dra. Mora", "mora@uleam.edu.ec", "POO", 20)
    sistema.registrar_usuario(docente)
    docente.agregar_disponibilidad("LUNES", time(7, 0), time(13, 0))

    gestor = GestorHorarios(periodo, list(sistema.aulas.values()))
    asignacion = gestor.crear_asignacion(sistema.nuevo_id("asignacion"), docente, poo, pa)
    gestor.crear_horario(sistema.nuevo_id("horario"), asignacion, "LUNES",
                         time(8, 0), time(10, 0), aula, "TEORIA")

    est1 = Estudiante(sistema.nuevo_id("usuario"), "Ana Pérez", "ana@uleam.edu.ec", "1311111111", "Software")
    est2 = Estudiante(sistema.nuevo_id("usuario"), "Luis Vera", "luis@uleam.edu.ec", "1322222222", "Software")
    sistema.registrar_usuario(est1)
    sistema.registrar_usuario(est2)

    def estado(estudiante):
        return [(m.id_matricula, m.estado, m.paralelo.codigo if m.paralelo else None)
                for m in estudiante.matriculas]

    fachada = FachadaMatricula(sistema)
    print("=== Facade: flujo de matrícula ===\n")

    print("1) Ana se matricula en A con UNA sola llamada:")
    m = fachada.matricular(est1.id, "a")
    print(f"   {m.estado} en {m.paralelo.codigo} | cupos {pa.numero_estudiantes}/{pa.cupo_maximo}")

    print("\n2) Luis intenta entrar a A (sin cupo): la operación falla y se deshace:")
    try:
        fachada.matricular(est2.id, "A")
    except ValueError as error:
        print(f"   Error: {error}")
    print(f"   Matrículas de Luis: {estado(est2)}  (sin matrícula pendiente colgada)")
    print(f"   Cupos de A: {pa.numero_estudiantes}/{pa.cupo_maximo}")

    print("\n3) Luis lo reintenta en B, ahora sí:")
    m = fachada.matricular(est2.id, "B")
    print(f"   {m.estado} en {m.paralelo.codigo}")

    print("\n4) Ana intenta matricularse otra vez (ya tiene una activa):")
    try:
        fachada.matricular(est1.id, "B")
    except ValueError as error:
        print(f"   Error: {error}")
    print(f"   Matrículas de Ana: {estado(est1)}")

    print("\n5) Pasos separados (como el menú): solicitar y luego confirmar con paralelo inexistente:")
    est3 = Estudiante(sistema.nuevo_id("usuario"), "Eva Cano", "eva@uleam.edu.ec", "1333333333", "Software")
    sistema.registrar_usuario(est3)
    fachada.solicitar_matricula(est3.id)
    try:
        fachada.confirmar_matricula(est3.id, "Z")
    except ValueError as error:
        print(f"   Error: {error}")
    print(f"   Matrículas de Eva: {estado(est3)}  (sigue PENDIENTE y sin paralelo)")

    print("\n6) Horario de Ana consultado por la fachada:")
    for horario in fachada.consultar_horario(est1.id):
        print(f"   {horario}")
