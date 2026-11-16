"""Patrón estructural Composite aplicado a la consulta de horarios de SCHOS.

Jerarquía natural del modelo:
    periodo -> paralelos -> asignaciones -> bloques (Horario)

Participantes
-------------
Componente -> ComponenteHorario  (interfaz común)
Hoja       -> BloqueHorario      (envuelve un Horario real, sin copiarlo)
Compuesto  -> GrupoHorario       (contiene hojas y/u otros grupos)
Cliente    -> ConsultaHorarios   (arma el árbol según estudiante, docente,
                                  paralelo o periodo)

Ejecución del ejemplo de uso (desde la carpeta raíz del proyecto):
    python -m servicios.consulta_horarios
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator


class ComponenteHorario(ABC):
    """Interfaz común: el cliente trata igual a un bloque que a un grupo."""

    def __init__(self, nombre: str):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del componente no puede estar vacío.")
        self.nombre = nombre.strip()

    @abstractmethod
    def bloques(self) -> Iterator:
        """Recorre todos los Horario contenidos (recursivamente)."""

    @abstractmethod
    def mostrar(self, nivel: int = 0) -> list[str]:
        """Líneas de texto con sangría según la profundidad."""

    def etiqueta_bloques(self) -> str:
        n = self.contar_bloques()
        return f"{n} bloque" if n == 1 else f"{n} bloques"

    def total_minutos(self) -> int:
        return sum(b.calcular_duracion() for b in self.bloques())

    def contar_bloques(self) -> int:
        return sum(1 for _ in self.bloques())


class BloqueHorario(ComponenteHorario):
    """HOJA: representa un único bloque; guarda la referencia al Horario."""

    def __init__(self, horario):
        if not hasattr(horario, "calcular_duracion"):
            raise ValueError("BloqueHorario necesita un Horario.")
        super().__init__(str(horario))
        self.horario = horario

    def bloques(self) -> Iterator:
        yield self.horario

    def mostrar(self, nivel: int = 0) -> list[str]:
        h = self.horario
        return [f"{'  ' * nivel}- {h} [{h.tipo_sesion}, {h.calcular_duracion()} min]"]


class GrupoHorario(ComponenteHorario):
    """COMPUESTO: agrupa otros componentes (bloques u otros grupos)."""

    def __init__(self, nombre: str, categoria: str = "Grupo"):
        super().__init__(nombre)
        self.categoria = categoria
        self._hijos: list[ComponenteHorario] = []

    @property
    def hijos(self) -> list[ComponenteHorario]:
        return list(self._hijos)

    def agregar(self, componente: ComponenteHorario) -> None:
        if not isinstance(componente, ComponenteHorario):
            raise ValueError("Solo se pueden agregar componentes de horario.")
        if componente is self or (isinstance(componente, GrupoHorario)
                                  and componente._contiene(self)):
            raise ValueError("No se puede crear un ciclo en la jerarquía.")
        if any(h is componente for h in self._hijos):
            raise ValueError("El componente ya está en el grupo.")
        self._hijos.append(componente)

    def quitar(self, componente: ComponenteHorario) -> None:
        for i, h in enumerate(self._hijos):
            if h is componente:
                del self._hijos[i]
                return
        raise ValueError("El componente no pertenece al grupo.")

    def _contiene(self, otro: ComponenteHorario) -> bool:
        return any(h is otro or (isinstance(h, GrupoHorario) and h._contiene(otro))
                   for h in self._hijos)

    def bloques(self) -> Iterator:
        for hijo in self._hijos:
            yield from hijo.bloques()

    def mostrar(self, nivel: int = 0) -> list[str]:
        lineas = [f"{'  ' * nivel}{self.categoria}: {self.nombre} "
                  f"({self.etiqueta_bloques()}, {self.total_minutos()} min)"]
        for hijo in self._hijos:
            lineas.extend(hijo.mostrar(nivel + 1))
        return lineas


class ConsultaHorarios:
    """Arma el árbol Composite de cada consulta con los objetos reales del sistema."""

    def __init__(self, periodo):
        if periodo is None:
            raise ValueError("La consulta necesita un periodo académico.")
        self._periodo = periodo

    @staticmethod
    def _grupo_asignacion(asignacion, incluir_docente=True) -> GrupoHorario:
        nombre = asignacion.asignatura.nombre
        if incluir_docente:
            nombre += f" - {asignacion.docente.nombre}"
        grupo = GrupoHorario(nombre, "Asignación")
        for horario in asignacion.horarios:
            grupo.agregar(BloqueHorario(horario))
        return grupo

    def _grupo_paralelo(self, paralelo) -> GrupoHorario:
        grupo = GrupoHorario(f"{paralelo.codigo} ({paralelo.jornada})", "Paralelo")
        for asignacion in paralelo.asignaciones:
            grupo.agregar(self._grupo_asignacion(asignacion))
        return grupo

    def por_periodo(self) -> GrupoHorario:
        raiz = GrupoHorario(self._periodo.nombre, "Periodo")
        for paralelo in self._periodo.paralelos:
            raiz.agregar(self._grupo_paralelo(paralelo))
        return raiz

    def por_paralelo(self, paralelo) -> GrupoHorario:
        if paralelo.periodo is not self._periodo:
            raise ValueError("El paralelo no es del periodo de la consulta.")
        return self._grupo_paralelo(paralelo)

    def por_docente(self, docente) -> GrupoHorario:
        raiz = GrupoHorario(docente.nombre, "Docente")
        for asignacion in docente.asignaciones:
            if asignacion.paralelo.periodo is self._periodo:
                grupo = self._grupo_asignacion(asignacion, incluir_docente=False)
                grupo.nombre += f" (paralelo {asignacion.paralelo.codigo})"
                raiz.agregar(grupo)
        return raiz

    def por_estudiante(self, estudiante) -> GrupoHorario:
        """Solo cuenta la matrícula CONFIRMADA, igual que Estudiante.ver_horario."""
        raiz = GrupoHorario(estudiante.nombre, "Estudiante")
        for matricula in estudiante.matriculas:
            if matricula.periodo is self._periodo and matricula.estado == "CONFIRMADA":
                raiz.agregar(self._grupo_paralelo(matricula.paralelo))
        return raiz


# --------------------------------------------------------------------------
# Ejemplo de uso
# --------------------------------------------------------------------------
if __name__ == "__main__":
    from datetime import date, time

    from aplicacion import SistemaSCHOS
    from modelos.academico.asignatura import Asignatura
    from modelos.academico.nivel import Nivel
    from modelos.academico.paralelo import Paralelo
    from modelos.academico.periodo_academico import PeriodoAcademico
    from modelos.aulas.aula_teorica import AulaTeorica
    from modelos.aulas.laboratorio import Laboratorio
    from modelos.usuarios.docente import Docente
    from modelos.usuarios.estudiante import Estudiante
    from servicios.fachada_matricula import FachadaMatricula
    from servicios.gestor_horarios import GestorHorarios

    sistema = SistemaSCHOS()
    periodo = PeriodoAcademico("2026-2", "Periodo 2026-2", date(2026, 11, 1), date(2027, 3, 31))
    periodo.abrir_periodo()
    sistema.establecer_periodo(periodo)

    nivel = Nivel(1, "Primer nivel")
    poo = Asignatura("POO-101", "Programación Orientada a Objetos", 4, 2, 2)
    bd = Asignatura("BD-101", "Bases de Datos", 3, 2, 0)
    nivel.agregar_asignatura(poo)
    nivel.agregar_asignatura(bd)
    pa = Paralelo("A", "MATUTINA", 30, nivel, periodo)
    pb = Paralelo("B", "VESPERTINA", 30, nivel, periodo)
    periodo.agregar_paralelo(pa)
    periodo.agregar_paralelo(pb)

    aula = AulaTeorica("A-101", 40, 1, True)
    lab = Laboratorio("LAB-1", 30, 0, True, "30 PC")
    sistema.registrar_aula(aula)
    sistema.registrar_aula(lab)

    mora = Docente(sistema.nuevo_id("usuario"), "Dra. Mora", "mora@uleam.edu.ec", "POO", 20)
    ruiz = Docente(sistema.nuevo_id("usuario"), "Ing. Ruiz", "ruiz@uleam.edu.ec", "BD", 20)
    for d in (mora, ruiz):
        sistema.registrar_usuario(d)
        for dia in ("LUNES", "MARTES", "MIERCOLES"):
            d.agregar_disponibilidad(dia, time(7, 0), time(18, 0))

    gestor = GestorHorarios(periodo, sistema.aulas)
    a1 = gestor.crear_asignacion(sistema.nuevo_id("asignacion"), mora, poo, pa)
    a2 = gestor.crear_asignacion(sistema.nuevo_id("asignacion"), ruiz, bd, pa)
    a3 = gestor.crear_asignacion(sistema.nuevo_id("asignacion"), mora, poo, pb)
    nh = lambda: sistema.nuevo_id("horario")
    gestor.crear_horario(nh(), a1, "LUNES", time(8, 0), time(10, 0), aula, "TEORIA")
    gestor.crear_horario(nh(), a1, "MARTES", time(8, 0), time(10, 0), lab, "PRACTICA")
    gestor.crear_horario(nh(), a2, "MIERCOLES", time(10, 0), time(12, 0), aula, "TEORIA")
    gestor.crear_horario(nh(), a3, "LUNES", time(14, 0), time(16, 0), aula, "TEORIA")

    ana = Estudiante(sistema.nuevo_id("usuario"), "Ana Pérez", "ana@uleam.edu.ec", "1311111111", "Software")
    sistema.registrar_usuario(ana)
    FachadaMatricula(sistema).matricular(ana.id, "A")

    consulta = ConsultaHorarios(periodo)

    def resumen(componente: ComponenteHorario) -> str:
        """Función cliente: no sabe si recibe una hoja o un grupo."""
        return (f"{componente.nombre}: {componente.etiqueta_bloques()}, "
                f"{componente.total_minutos()} min")

    print("=== Composite: consultas de horarios ===")
    for titulo, arbol in [
        ("Por periodo", consulta.por_periodo()),
        ("Por paralelo A", consulta.por_paralelo(pa)),
        ("Por docente (Dra. Mora)", consulta.por_docente(mora)),
        ("Por estudiante (Ana)", consulta.por_estudiante(ana)),
    ]:
        print(f"\n--- {titulo} ---")
        print("\n".join(arbol.mostrar()))

    print("\n--- Tratamiento uniforme: la misma función con hoja y con grupos ---")
    arbol = consulta.por_periodo()
    paralelo_a = arbol.hijos[0]
    asignacion_poo = paralelo_a.hijos[0]
    hoja = asignacion_poo.hijos[0]
    for nodo in (hoja, asignacion_poo, paralelo_a, arbol):
        print(f"{type(nodo).__name__:<14} -> {resumen(nodo)}")

    print("\n--- Los bloques son los mismos objetos del sistema (no copias) ---")
    originales = [h for p in periodo.paralelos for a in p.asignaciones for h in a.horarios]
    del_arbol = list(arbol.bloques())
    print("Misma cantidad:", len(originales) == len(del_arbol),
          "| Mismas instancias:", all(x is y for x, y in zip(originales, del_arbol)))
