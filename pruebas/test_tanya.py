import unittest
from datetime import date, time

from modelos.academico.asignacion_academica import AsignacionAcademica
from modelos.academico.asignatura import Asignatura
from modelos.academico.nivel import Nivel
from modelos.academico.paralelo import Paralelo
from modelos.academico.periodo_academico import PeriodoAcademico
from modelos.aulas.aula_teorica import AulaTeorica
from modelos.horarios.horario import Horario
from modelos.usuarios.administrador import Administrador
from modelos.usuarios.docente import Docente
from modelos.usuarios.estudiante import Estudiante
from modelos.usuarios.usuario import Usuario


def crear_periodo(codigo="2026-1", abierto=True):
    periodo = PeriodoAcademico(codigo, "Periodo de prueba", date(2026, 10, 1), date(2027, 2, 28))
    if abierto:
        periodo.abrir_periodo()
    return periodo


def crear_docente(max_horas=4):
    return Docente(1, "Docente Uno", "d1@uleam.edu.ec", "Programación", max_horas)


def crear_estudiante(n=1):
    return Estudiante(100 + n, f"Estudiante {n}", f"est{n}@uleam.edu.ec", f"130000000{n}", "Software")


class EscenarioBase(unittest.TestCase):
    def setUp(self):
        self.periodo = crear_periodo()
        self.nivel = Nivel(1, "Primero")
        self.paralelo = Paralelo("A", "MATUTINA", 1, self.nivel, self.periodo)
        self.periodo.agregar_paralelo(self.paralelo)
        self.est1 = crear_estudiante(1)
        self.est2 = crear_estudiante(2)
        
class TestUsuarios(unittest.TestCase):
    def test_usuario_es_abstracto(self):
        with self.assertRaises(TypeError):
            Usuario(1, "Ana", "ana@uleam.edu.ec")

    def test_clases_concretas_se_crean(self):
        admin = Administrador(1, "Ada", "ada@uleam.edu.ec")
        docente = crear_docente()
        estudiante = crear_estudiante()
        self.assertEqual(admin.rol, "COORDINADOR")
        self.assertEqual(docente.especialidad, "Programación")
        self.assertEqual(estudiante.cedula, "1300000001")
        for usuario in (admin, docente, estudiante):
            self.assertIsInstance(usuario, Usuario)

    def test_validaciones_de_datos(self):
        datos_malos = [(0, "Ana", "a@b.com"), (-1, "Ana", "a@b.com"),
                       (1, "  ", "a@b.com"), (1, "Ana", "sin-arroba"), (1, "Ana", "a@b")]
        for datos in datos_malos:
            with self.assertRaises(ValueError):
                Administrador(*datos)
        with self.assertRaises(ValueError):
            Docente(1, "Ana", "a@b.com", "POO", 0)
        with self.assertRaises(ValueError):
            Docente(1, "Ana", "a@b.com", "", 4)


class TestEstudiante(unittest.TestCase):
    def test_cedula_invalida(self):
        for cedula in ("123456789", "12345678901", "13000000a1"):
            with self.assertRaises(ValueError):
                Estudiante(1, "Ana", "a@b.com", cedula, "Software")

    def test_carrera_vacia(self):
        with self.assertRaises(ValueError):
            Estudiante(1, "Ana", "a@b.com", "1300000001", "  ")


class TestDocente(EscenarioBase):
    def setUp(self):
        super().setUp()
        self.docente = crear_docente(max_horas=2)
        self.mat_a = Asignatura("POO", "POO", 3, 2, 0)            #2 horas
        self.mat_b = Asignatura("BD", "Bases de datos", 3, 1, 0)  #1 hora
        self.asig_a = AsignacionAcademica(1, self.docente, self.mat_a, self.paralelo)
        self.asig_b = AsignacionAcademica(2, self.docente, self.mat_b, self.paralelo)

    def test_carga_maxima_rechaza_sin_anadir(self):
        self.docente.asignar_asignatura(self.asig_a)
        self.assertEqual(self.docente.horas_asignadas(self.periodo), 2)
        with self.assertRaises(ValueError):
            self.docente.asignar_asignatura(self.asig_b)
        # el rechazo no cambió nada
        self.assertEqual(self.docente.asignaciones, [self.asig_a])
        self.assertEqual(self.docente.horas_asignadas(self.periodo), 2)

    def test_asignar_duplicada_o_ajena(self):
        docente = crear_docente(max_horas=10)
        asig = AsignacionAcademica(1, docente, self.mat_a, self.paralelo)
        docente.asignar_asignatura(asig)
        with self.assertRaises(ValueError):
            docente.asignar_asignatura(asig)  #repetida
        otro = Docente(2, "Otro", "o@uleam.edu.ec", "Redes", 10)
        with self.assertRaises(ValueError):
            otro.asignar_asignatura(asig)     #es de otro docente
        self.assertEqual(otro.asignaciones, [])
        self.assertEqual(len(docente.asignaciones), 1)

    def test_quitar_asignacion(self):
        self.docente.asignar_asignatura(self.asig_a)
        self.docente.quitar_asignacion(self.asig_a)
        self.assertEqual(self.docente.asignaciones, [])
        with self.assertRaises(ValueError):
            self.docente.quitar_asignacion(self.asig_a)

    def test_disponibilidad(self):
        d = self.docente
        d.agregar_disponibilidad("LUNES", time(8), time(12))
        d.agregar_disponibilidad("LUNES", time(15), time(17))
        self.assertTrue(d.esta_disponible("LUNES", time(8), time(10)))
        self.assertTrue(d.esta_disponible("LUNES", time(15), time(17)))
        self.assertFalse(d.esta_disponible("LUNES", time(11), time(13)))  #se sale
        self.assertFalse(d.esta_disponible("LUNES", time(12), time(15)))  #en el hueco
        self.assertFalse(d.esta_disponible("MARTES", time(8), time(10)))
        with self.assertRaises(ValueError):
            d.agregar_disponibilidad("LUNES", time(12), time(8))  #invertida
        self.assertEqual(len(d.disponibilidades), 2)
        d.disponibilidades.clear()  #es una copia, no cambia la original
        self.assertEqual(len(d.disponibilidades), 2)


class TestAdministrador(EscenarioBase):
    def setUp(self):
        super().setUp()
        self.admin = Administrador(9, "Ada", "ada@uleam.edu.ec")

    def test_abrir_paralelo(self):
        p = self.admin.abrir_paralelo(self.periodo, self.nivel, "B", "MATUTINA", 30)
        self.assertEqual(p.codigo, "B")
        self.assertIn(p, self.periodo.paralelos)

    def test_abrir_paralelo_rechazos_no_dejan_rastro(self):
        antes = self.periodo.paralelos
        with self.assertRaises(ValueError):
            self.admin.abrir_paralelo(self.periodo, self.nivel, "Z", "MATUTINA", 0)  # cupo 0
        self.assertEqual(self.periodo.paralelos, antes)
        planificado = crear_periodo("2026-2", abierto=False)
        with self.assertRaises(ValueError):
            self.admin.abrir_paralelo(planificado, self.nivel, "A", "MATUTINA", 30)
        self.assertEqual(planificado.paralelos, [])


class TestMatricula(EscenarioBase):
    def test_dos_solicitudes_activas_fallan(self):
        self.est1.solicitar_matricula(self.periodo, 1)
        with self.assertRaises(ValueError):
            self.est1.solicitar_matricula(self.periodo, 2)
        self.assertEqual(len(self.est1.matriculas), 1)

    def test_solicitar_en_periodo_no_abierto(self):
        planificado = crear_periodo("2026-2", abierto=False)
        with self.assertRaises(ValueError):
            self.est1.solicitar_matricula(planificado, 1)
        self.assertEqual(self.est1.matriculas, [])

    def test_elegir_no_ocupa_cupo_y_confirmar_si(self):
        m = self.est1.solicitar_matricula(self.periodo, 1)
        self.assertEqual(m.estado, "PENDIENTE")
        self.assertIs(self.est1.matricular(self.paralelo), m)
        self.assertEqual(self.paralelo.numero_estudiantes, 0)
        m.confirmar()
        self.assertEqual(m.estado, "CONFIRMADA")
        self.assertEqual(self.paralelo.numero_estudiantes, 1)

    def test_confirmar_dos_veces_no_duplica(self):
        m = self.est1.solicitar_matricula(self.periodo, 1)
        self.est1.matricular(self.paralelo)
        m.confirmar()
        with self.assertRaises(ValueError):
            m.confirmar()
        self.assertEqual(self.paralelo.estudiantes, [self.est1])

    def test_confirmar_sin_paralelo(self):
        m = self.est1.solicitar_matricula(self.periodo, 1)
        with self.assertRaises(ValueError):
            m.confirmar()
        self.assertEqual(m.estado, "PENDIENTE")

    def test_confirmar_sin_cupo(self):
        m1 = self.est1.solicitar_matricula(self.periodo, 1)
        self.est1.matricular(self.paralelo)
        m1.confirmar()
        m2 = self.est2.solicitar_matricula(self.periodo, 2)
        self.est2.matricular(self.paralelo)  #elegir sí se permite con el cupo lleno
        with self.assertRaises(ValueError):
            m2.confirmar()
        self.assertEqual(m2.estado, "PENDIENTE")
        self.assertEqual(self.paralelo.numero_estudiantes, 1)

    def test_cancelar_confirmada_libera_un_cupo_una_sola_vez(self):
        m1 = self.est1.solicitar_matricula(self.periodo, 1)
        self.est1.matricular(self.paralelo)
        m1.confirmar()
        m1.cancelar()
        self.assertEqual(m1.estado, "CANCELADA")
        self.assertEqual(self.paralelo.numero_estudiantes, 0)
        with self.assertRaises(ValueError):
            m1.cancelar()  # ya estaba cancelada
        self.assertEqual(self.paralelo.numero_estudiantes, 0)
        # el cupo liberado lo puede usar otro estudiante
        m2 = self.est2.solicitar_matricula(self.periodo, 2)
        self.est2.matricular(self.paralelo)
        m2.confirmar()
        self.assertEqual(self.paralelo.estudiantes, [self.est2])

    def test_cancelar_pendiente_y_pedir_otra(self):
        m = self.est1.solicitar_matricula(self.periodo, 1)
        self.est1.matricular(self.paralelo)
        m.cancelar()
        self.assertEqual(self.paralelo.numero_estudiantes, 0)
        nueva = self.est1.solicitar_matricula(self.periodo, 2)
        self.assertEqual(nueva.estado, "PENDIENTE")

    def test_paralelo_de_otro_periodo_o_no_registrado(self):
        otro_periodo = crear_periodo("2026-X")
        ajeno = Paralelo("B", "MATUTINA", 1, self.nivel, otro_periodo)
        otro_periodo.agregar_paralelo(ajeno)
        sin_registrar = Paralelo("C", "MATUTINA", 1, self.nivel, self.periodo)
        m = self.est1.solicitar_matricula(self.periodo, 1)
        self.est1.matricular(self.paralelo)
        for paralelo in (ajeno, sin_registrar):
            with self.assertRaises(ValueError):
                m.agregar_paralelo(paralelo)
            self.assertIs(m.paralelo, self.paralelo)#la elección anterior se conserva

    def test_matricular_sin_solicitud_falla(self):
        with self.assertRaises(ValueError):
            self.est1.matricular(self.paralelo)

    def test_periodo_cerrado_bloquea_cambios(self):
        m = self.est1.solicitar_matricula(self.periodo, 1)
        self.est1.matricular(self.paralelo)
        m.confirmar()
        self.periodo.cerrar_periodo()
        with self.assertRaises(ValueError):
            m.cancelar()
        self.assertEqual(m.estado, "CONFIRMADA")
        self.assertEqual(self.paralelo.numero_estudiantes, 1)


class TestHorarios(EscenarioBase):
    def setUp(self):
        super().setUp()
        self.docente = crear_docente()
        self.admin = Administrador(9, "Ada", "ada@uleam.edu.ec")
        asignatura = Asignatura("POO", "POO", 3, 2, 0)
        self.nivel.agregar_asignatura(asignatura)
        asignacion = AsignacionAcademica(1, self.docente, asignatura, self.paralelo)
        self.docente.asignar_asignatura(asignacion)
        self.paralelo.agregar_asignacion(asignacion)
        self.bloque = Horario(1, "LUNES", time(8), time(10), AulaTeorica("A101", 2, 1, True), "TEORIA")
        asignacion.agregar_horario(self.bloque)

    def test_administrador_y_docente_ven_el_bloque(self):
        self.assertEqual(self.admin.ver_horario(self.periodo), [self.bloque])
        self.assertEqual(self.docente.ver_horario(self.periodo), [self.bloque])
        self.assertEqual(self.docente.consultar_horario(self.periodo), [self.bloque])
        self.assertEqual(self.docente.ver_horario(crear_periodo("OTRO")), [])

    def test_estudiante_solo_ve_horario_confirmado(self):
        m = self.est1.solicitar_matricula(self.periodo, 1)
        self.est1.matricular(self.paralelo)
        self.assertEqual(self.est1.ver_horario(self.periodo), [])  # pendiente
        m.confirmar()
        self.assertEqual(self.est1.ver_horario(self.periodo), [self.bloque])
        m.cancelar()
        self.assertEqual(self.est1.ver_horario(self.periodo), [])  # cancelada


if __name__ == "__main__":
    unittest.main()