"""Builder para construir escenarios completos de SCHOS por etapas.

Ejecución del ejemplo desde la raíz del repositorio:
    py -m servicios.constructor_sistema
"""

from datetime import date, time

from aplicacion import SistemaSCHOS
from modelos.academico.asignacion_academica import AsignacionAcademica
from modelos.academico.asignatura import Asignatura
from modelos.academico.nivel import Nivel
from modelos.academico.paralelo import Paralelo
from modelos.academico.periodo_academico import PeriodoAcademico
from modelos.aulas.aula import Aula
from modelos.usuarios.docente import Docente
from modelos.usuarios.estudiante import Estudiante
from servicios.fachada_matricula import FachadaMatricula
from servicios.gestor_horarios import GestorHorarios
from servicios.registro_aulas import ServicioRegistroAulas
from modelos.aulas.creadores.catalogo_creadores import crear_catalogo_por_defecto


class SistemaSCHOSBuilder:
    """Construye el objeto SistemaSCHOS y sus relaciones de forma gradual."""

    def __init__(self):
        self._sistema = SistemaSCHOS()
        self._registro_aulas = ServicioRegistroAulas(
            self._sistema,
            crear_catalogo_por_defecto(),
        )
        self._construido = False

    def _verificar_disponible(self):
        if self._construido:
            raise ValueError("Este builder ya construyó el sistema.")

    def agregar_aula(
        self,
        tipo,
        codigo,
        capacidad,
        piso,
        tiene_proyector,
        **extras,
    ) -> Aula:
        self._verificar_disponible()
        return self._registro_aulas.registrar_aula(
            tipo,
            codigo,
            capacidad,
            piso,
            tiene_proyector,
            **extras,
        )

    def agregar_asignatura(
        self,
        codigo,
        nombre,
        creditos,
        horas_teoricas,
        horas_practicas,
        descripcion="",
    ) -> Asignatura:
        self._verificar_disponible()
        asignatura = Asignatura(
            codigo,
            nombre,
            creditos,
            horas_teoricas,
            horas_practicas,
            descripcion,
        )
        self._sistema.registrar_asignatura(asignatura)
        return asignatura

    def agregar_nivel(self, numero, nombre, codigos_asignaturas=()) -> Nivel:
        self._verificar_disponible()

        codigos = [codigo.strip().upper() for codigo in codigos_asignaturas]
        if len(codigos) != len(set(codigos)):
            raise ValueError("No repitas asignaturas al crear el nivel.")

        asignaturas = []
        for codigo in codigos:
            if codigo not in self._sistema.asignaturas:
                raise ValueError(f"No existe la asignatura {codigo}.")
            asignaturas.append(self._sistema.asignaturas[codigo])

        nivel = Nivel(numero, nombre)
        for asignatura in asignaturas:
            nivel.agregar_asignatura(asignatura)

        self._sistema.registrar_nivel(nivel)
        return nivel

    def agregar_docente(
        self,
        nombre,
        correo,
        especialidad,
        max_horas_semanales,
        disponibilidades=(),
    ) -> Docente:
        self._verificar_disponible()

        docente = Docente(
            self._sistema.nuevo_id("usuario"),
            nombre,
            correo,
            especialidad,
            max_horas_semanales,
        )

        for dia, hora_inicio, hora_fin in disponibilidades:
            docente.agregar_disponibilidad(dia, hora_inicio, hora_fin)

        self._sistema.registrar_usuario(docente)
        return docente

    def agregar_estudiante(self, nombre, correo, cedula, carrera) -> Estudiante:
        self._verificar_disponible()
        estudiante = Estudiante(
            self._sistema.nuevo_id("usuario"),
            nombre,
            correo,
            cedula,
            carrera,
        )
        self._sistema.registrar_usuario(estudiante)
        return estudiante

    def establecer_periodo(self, codigo, nombre, fecha_inicio, fecha_fin):
        self._verificar_disponible()
        periodo = PeriodoAcademico(
            codigo,
            nombre,
            fecha_inicio,
            fecha_fin,
        )
        self._sistema.establecer_periodo(periodo)
        return periodo

    def abrir_periodo(self):
        self._verificar_disponible()
        if self._sistema.periodo is None:
            raise ValueError("Primero debes establecer el periodo.")
        self._sistema.periodo.abrir_periodo()
        return self

    def agregar_paralelo(
        self,
        codigo,
        jornada,
        cupo_maximo,
        numero_nivel,
    ) -> Paralelo:
        self._verificar_disponible()

        periodo = self._sistema.periodo
        if periodo is None:
            raise ValueError("Primero debes establecer el periodo.")

        if numero_nivel not in self._sistema.niveles:
            raise ValueError(f"No existe el nivel {numero_nivel}.")

        paralelo = Paralelo(
            codigo,
            jornada,
            cupo_maximo,
            self._sistema.niveles[numero_nivel],
            periodo,
        )
        periodo.agregar_paralelo(paralelo)
        return paralelo

    def crear_asignacion(
        self,
        id_docente,
        codigo_asignatura,
        codigo_paralelo,
    ) -> AsignacionAcademica:
        self._verificar_disponible()

        docente = self._sistema.usuarios.get(id_docente)
        if not isinstance(docente, Docente):
            raise ValueError(f"No existe el docente con ID {id_docente}.")

        codigo_asignatura = codigo_asignatura.strip().upper()
        asignatura = self._sistema.asignaturas.get(codigo_asignatura)
        if asignatura is None:
            raise ValueError(f"No existe la asignatura {codigo_asignatura}.")

        paralelo = self._buscar_paralelo(codigo_paralelo)
        gestor = GestorHorarios(
            self._sistema.periodo,
            self._sistema.aulas,
        )
        return gestor.crear_asignacion(
            self._sistema.nuevo_id("asignacion"),
            docente,
            asignatura,
            paralelo,
        )

    def agregar_horario(
        self,
        id_asignacion,
        dia,
        hora_inicio,
        hora_fin,
        codigo_aula,
        tipo_sesion,
    ):
        self._verificar_disponible()

        asignacion = self._buscar_asignacion(id_asignacion)
        codigo_aula = codigo_aula.strip().upper()
        aula = self._sistema.aulas.get(codigo_aula)
        if aula is None:
            raise ValueError(f"No existe el aula {codigo_aula}.")

        gestor = GestorHorarios(
            self._sistema.periodo,
            self._sistema.aulas,
        )
        return gestor.crear_horario(
            self._sistema.nuevo_id("horario"),
            asignacion,
            dia,
            hora_inicio,
            hora_fin,
            aula,
            tipo_sesion,
        )

    def matricular(self, id_estudiante, codigo_paralelo):
        self._verificar_disponible()
        return FachadaMatricula(self._sistema).matricular(
            id_estudiante,
            codigo_paralelo,
        )

    def construir(self) -> SistemaSCHOS:
        self._verificar_disponible()
        self._construido = True
        return self._sistema

    def _buscar_paralelo(self, codigo):
        if self._sistema.periodo is None:
            raise ValueError("Primero debes establecer el periodo.")

        buscado = codigo.strip().upper()
        for paralelo in self._sistema.periodo.paralelos:
            if paralelo.codigo == buscado:
                return paralelo
        raise ValueError(f"No existe el paralelo {buscado}.")

    def _buscar_asignacion(self, id_asignacion):
        if self._sistema.periodo is None:
            raise ValueError("Primero debes establecer el periodo.")

        for paralelo in self._sistema.periodo.paralelos:
            for asignacion in paralelo.asignaciones:
                if asignacion.id_asignacion == id_asignacion:
                    return asignacion
        raise ValueError(f"No existe la asignación {id_asignacion}.")


if __name__ == "__main__":
    builder = SistemaSCHOSBuilder()

    builder.agregar_asignatura(
        "POO-101",
        "Programación Orientada a Objetos",
        4,
        horas_teoricas=2,
        horas_practicas=2,
    )
    builder.agregar_nivel(
        1,
        "Primer nivel",
        codigos_asignaturas=("POO-101",),
    )

    aula_teorica = builder.agregar_aula(
        "TEORICA",
        "A-101",
        30,
        1,
        True,
    )
    laboratorio = builder.agregar_aula(
        "LABORATORIO",
        "L-101",
        30,
        1,
        True,
        equipamiento="Computadoras",
    )

    docente = builder.agregar_docente(
        "Dra. Mora",
        "mora@uleam.edu.ec",
        "Programación",
        5,
        disponibilidades=(
            ("LUNES", time(7, 0), time(13, 0)),
            ("MARTES", time(7, 0), time(13, 0)),
        ),
    )
    estudiante = builder.agregar_estudiante(
        "Ana Pérez",
        "ana@uleam.edu.ec",
        "1300000001",
        "Software",
    )

    builder.establecer_periodo(
        "2026-2",
        "Periodo 2026-2",
        date(2026, 11, 16),
        date(2027, 3, 31),
    )
    builder.abrir_periodo()

    paralelo = builder.agregar_paralelo(
        "A",
        "MATUTINA",
        25,
        numero_nivel=1,
    )
    asignacion = builder.crear_asignacion(
        docente.id,
        "POO-101",
        "A",
    )

    builder.agregar_horario(
        asignacion.id_asignacion,
        "LUNES",
        time(8, 0),
        time(10, 0),
        aula_teorica.codigo_aula,
        "TEORIA",
    )
    builder.agregar_horario(
        asignacion.id_asignacion,
        "MARTES",
        time(8, 0),
        time(10, 0),
        laboratorio.codigo_aula,
        "PRACTICA",
    )

    matricula = builder.matricular(estudiante.id, paralelo.codigo)
    sistema = builder.construir()

    print("Sistema SCHOS construido.")
    print(f"Usuarios: {len(sistema.usuarios)}")
    print(f"Aulas: {len(sistema.aulas)}")
    print(f"Asignaturas: {len(sistema.asignaturas)}")
    print(f"Paralelos: {len(sistema.periodo.paralelos)}")
    print(f"Bloques en el horario: {len(asignacion.horarios)}")
    print(f"Matrícula: {matricula.estado} en el paralelo {matricula.paralelo.codigo}")