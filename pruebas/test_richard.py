import itertools
import unittest
from datetime import date, time as T

from modelos.academico.asignacion_academica import AsignacionAcademica
from modelos.academico.asignatura import Asignatura
from modelos.academico.nivel import Nivel
from modelos.academico.paralelo import Paralelo
from modelos.academico.periodo_academico import PeriodoAcademico
from modelos.aulas.aula_teorica import AulaTeorica
from modelos.aulas.laboratorio import Laboratorio
from modelos.horarios.horario import Horario
from modelos.usuarios.administrador import Administrador
from modelos.usuarios.docente import Docente
from servicios.gestor_horarios import GestorHorarios

LUN_8_12 = [("LUNES", T(8, 0), T(12, 0))]
_ids = itertools.count(1)


def nuevo_periodo(codigo="2026-2"):
    return PeriodoAcademico(codigo, "Periodo de prueba", date(2026, 9, 1), date(2027, 2, 1))


def nuevo_docente(max_horas=4, disponibilidad=LUN_8_12):
    n = next(_ids)
    d = Docente(n, f"Docente {n}", f"docente{n}@correo.com", "Software", max_horas)
    for dia, ini, fin in disponibilidad:
        d.agregar_disponibilidad(dia, ini, fin)
    return d

class TestHorario(unittest.TestCase):
    def setUp(self):
        self.aula = AulaTeorica("A101", 2, 1, True)

    def test_valido_y_duracion(self):
        h = Horario(1, "lunes", T(8, 0), T(9, 30), self.aula, "teoria")
        self.assertEqual((h.dia, h.tipo_sesion, h.calcular_duracion()), ("LUNES", "TEORIA", 90))

    def test_dia_con_tilde_se_normaliza(self):
        self.assertEqual(Horario(1, "Miércoles", T(8), T(9), self.aula, "TEORIA").dia, "MIERCOLES")

    def test_rechazos_de_constructor(self):
        casos = [
            (0, "LUNES", T(8), T(9), self.aula, "TEORIA"),
            (1, "SABADO", T(8), T(9), self.aula, "TEORIA"),
            (1, "LUNES", T(12), T(8), self.aula, "TEORIA"),
            (1, "LUNES", T(8), T(8), self.aula, "TEORIA"),
            (1, "LUNES", T(8, 0, 30), T(9), self.aula, "TEORIA"),
            (1, "LUNES", T(8), T(9), None, "TEORIA"),
            (1, "LUNES", T(8), T(9), self.aula, "OTRO"),
            (1, "LUNES", "08:00", T(9), self.aula, "TEORIA"),
        ]
        for c in casos:
            with self.subTest(c), self.assertRaises(ValueError):
                Horario(*c)

    def test_contiguos_no_chocan_y_solapados_si(self):
        a = Horario(1, "LUNES", T(8), T(10), self.aula, "TEORIA")
        b = Horario(2, "LUNES", T(10), T(12), self.aula, "TEORIA")
        c = Horario(3, "LUNES", T(9), T(11), self.aula, "TEORIA")
        d = Horario(4, "MARTES", T(8), T(10), self.aula, "TEORIA")
        self.assertFalse(a.detectar_conflicto(b))
        self.assertTrue(a.detectar_conflicto(c))
        self.assertFalse(a.detectar_conflicto(d))

    def test_exportar_y_str(self):
        h = Horario(1, "LUNES", T(8), T(10), self.aula, "TEORIA")
        self.assertTrue(str(h).startswith("LUNES 08:00-10:00"))
        ruta = h.exportar()
        try:
            self.assertEqual(ruta.read_text(encoding="utf-8"), str(h))
        finally:
            ruta.unlink()
        self.assertEqual(h.nube, "")
        self.assertTrue(h.validar_disponibilidad())

    def test_aplicar_cambios_invalido_no_altera(self):
        h = Horario(1, "LUNES", T(8), T(10), self.aula, "TEORIA")
        antes = h.datos()
        with self.assertRaises(ValueError):
            h.aplicar_cambios("LUNES", T(12), T(8), self.aula, "TEORIA")
        self.assertEqual(h.datos(), antes)

class TestAsignacion(unittest.TestCase):
    def setUp(self):
        periodo = nuevo_periodo()
        self.poo = Asignatura("POO", "Programación Orientada a Objetos", 4, 2, 2)
        nivel = Nivel(1, "Primer nivel")
        nivel.agregar_asignatura(self.poo)
        self.paralelo = Paralelo("A", "MATUTINA", 2, nivel, periodo)
        self.docente = nuevo_docente()
        self.asig = AsignacionAcademica(1, self.docente, self.poo, self.paralelo)
        self.aula = AulaTeorica("A101", 2, 1, True)

    def test_horas_semanales_y_copia(self):
        self.assertEqual(self.asig.horas_semanales, 4)
        self.asig.horarios.append("basura")
        self.assertEqual(self.asig.horarios, [])

    def test_agregar_quitar_y_rechazos(self):
        h = Horario(1, "LUNES", T(8), T(10), self.aula, "TEORIA")
        self.asig.agregar_horario(h)
        with self.assertRaises(ValueError):
            self.asig.agregar_horario(Horario(1, "LUNES", T(10), T(11), self.aula, "TEORIA"))
        self.assertEqual(len(self.asig.horarios), 1)       # el rechazo no alteró el estado
        self.asig.quitar_horario(h)
        with self.assertRaises(ValueError):
            self.asig.quitar_horario(h)

    def test_id_invalido(self):
        with self.assertRaises(ValueError):
            AsignacionAcademica(0, self.docente, self.poo, self.paralelo)

class BaseGestor(unittest.TestCase):

    def setUp(self):
        self.escenario(("A", "MATUTINA"))
        self.d1 = nuevo_docente(4)
        self.asig = self.asignar(1, self.d1, "A")

    def escenario(self, *paralelos):
        self.periodo = nuevo_periodo()
        self.poo = Asignatura("POO", "Programación Orientada a Objetos", 4, 2, 2)
        self.nivel = Nivel(1, "Primer nivel")
        self.nivel.agregar_asignatura(self.poo)
        self.par = {}
        for codigo, jornada in paralelos:
            p = Paralelo(codigo, jornada, 2, self.nivel, self.periodo)
            self.periodo.agregar_paralelo(p)
            self.par[codigo] = p
        self.periodo.abrir_periodo()
        self.a101 = AulaTeorica("A101", 2, 1, True)
        self.a102 = AulaTeorica("A102", 1, 1, True)      
        self.a103 = AulaTeorica("A103", 2, 1, True)
        self.l101 = Laboratorio("L101", 2, 1, True, "10 PCs")
        self.gestor = GestorHorarios(self.periodo, [self.a101, self.a102, self.a103, self.l101])

    def asignar(self, id_, docente, codigo, asignatura=None):
        return self.gestor.crear_asignacion(id_, docente, asignatura or self.poo, self.par[codigo])

    def teoria(self, id_, ini=T(8), fin=T(10), aula=None, asig=None):
        return self.gestor.crear_horario(id_, asig or self.asig, "LUNES", ini, fin, aula or self.a101, "TEORIA")

    def practica(self, id_, ini=T(10), fin=T(12), aula=None):
        return self.gestor.crear_horario(id_, self.asig, "LUNES", ini, fin, aula or self.l101, "PRACTICA")

class TestCrearAsignacion(BaseGestor):
    def test_se_registra_en_docente_y_paralelo(self):
        self.assertIn(self.asig, self.d1.asignaciones)
        self.assertIn(self.asig, self.par["A"].asignaciones)

    def test_carga_docente_excedida_no_agrega_nada(self):
        self.escenario(("A", "MATUTINA"), ("B", "MATUTINA"))
        d = nuevo_docente(4)
        self.asignar(1, d, "A")                                       
        with self.assertRaisesRegex(ValueError, "máximo"):
            self.asignar(2, d, "B")                                   
        self.assertEqual(self.par["B"].asignaciones, [])
        self.assertEqual(len(d.asignaciones), 1)

    def test_rechazos(self):
        otra = Asignatura("MAT", "Matemática", 3, 1, 0)
        ajeno = Paralelo("Z", "MATUTINA", 2, self.nivel, nuevo_periodo("2027-1"))
        casos = [
            (2, self.d1, self.poo, self.par["A"]),   # materia repetida en el paralelo
            (2, self.d1, otra, self.par["A"]),       # materia que no es del nivel
            (2, self.d1, self.poo, ajeno),           # paralelo de otro periodo
            (1, self.d1, self.poo, self.par["A"]),   # ID repetido
        ]
        for c in casos:
            with self.subTest(id=c[0], materia=c[2].codigo, paralelo=c[3].codigo), self.assertRaises(ValueError):
                self.gestor.crear_asignacion(*c)
        self.assertEqual(len(self.par["A"].asignaciones), 1)
        self.assertEqual(len(self.d1.asignaciones), 1)

class TestCrearHorario(BaseGestor):
    def test_contiguos_se_aceptan(self):
        self.teoria(1)
        self.practica(2)
        self.assertEqual(len(self.asig.horarios), 2)
        self.assertEqual(len(self.a101.reservas), 1)
        self.assertEqual(len(self.l101.reservas), 1)

    def test_rechazo_no_deja_reserva(self):
        self.teoria(1)
        with self.assertRaises(ValueError):
            self.practica(2, T(9), T(11))                
        self.assertEqual(self.l101.reservas, [])
        self.assertEqual(len(self.asig.horarios), 1)

    def test_aula_compartida_docentes_distintos(self):
        self.escenario(("A", "MATUTINA"), ("B", "MATUTINA"))
        asig_a = self.asignar(1, nuevo_docente(), "A")
        asig_b = self.asignar(2, nuevo_docente(), "B")
        self.teoria(1, aula=self.a101, asig=asig_a)
        with self.assertRaisesRegex(ValueError, "ocupada"):
            self.teoria(2, aula=self.a101, asig=asig_b)
        self.assertEqual(asig_b.horarios, [])

    def test_docente_compartido_aulas_distintas(self):
        self.escenario(("A", "MATUTINA"), ("B", "MATUTINA"))
        doc = nuevo_docente(8)
        asig_a = self.asignar(1, doc, "A")
        asig_b = self.asignar(2, doc, "B")
        self.teoria(1, aula=self.a101, asig=asig_a)
        with self.assertRaisesRegex(ValueError, "docente"):
            self.teoria(2, aula=self.a103, asig=asig_b)
        self.assertEqual(self.a103.reservas, [])

    def test_mismo_paralelo_recursos_distintos(self):
        mat = Asignatura("MAT", "Matemática", 3, 2, 0)
        self.nivel.agregar_asignatura(mat)
        asig_m = self.asignar(2, nuevo_docente(), "A", mat)
        self.teoria(1, aula=self.a101)
        with self.assertRaisesRegex(ValueError, "paralelo"):
            self.teoria(2, aula=self.a103, asig=asig_m)
        self.assertEqual(self.a103.reservas, [])

    def test_paralelos_distintos_recursos_distintos_pueden_coincidir(self):
        self.escenario(("A", "MATUTINA"), ("B", "MATUTINA"))
        asig_a = self.asignar(1, nuevo_docente(), "A")
        asig_b = self.asignar(2, nuevo_docente(), "B")
        self.teoria(1, aula=self.a101, asig=asig_a)
        self.teoria(2, aula=self.a103, asig=asig_b)       
        self.assertEqual(len(asig_b.horarios), 1)

    def test_jornada_y_tipo(self):
        self.escenario(("A", "MATUTINA"), ("N", "NOCTURNA"))
        asig_n = self.asignar(1, nuevo_docente(4, [("LUNES", T(7), T(12))]), "N")
        asig_a = self.asignar(2, nuevo_docente(), "A")
        with self.assertRaisesRegex(ValueError, "jornada"):
            self.teoria(1, T(7), T(9), asig=asig_n)       
        with self.assertRaisesRegex(ValueError, "no admite"):
            self.gestor.crear_horario(2, asig_a, "LUNES", T(8), T(10), self.a101, "PRACTICA")
        self.assertEqual(self.a101.reservas, [])

    def test_capacidad_y_equipamiento(self):
        with self.assertRaisesRegex(ValueError, "capacidad"):
            self.teoria(1, aula=self.a102)
        sin_equipo = Laboratorio("L102", 2, 1, True, "PCs")
        sin_equipo.equipamiento = ""                      
        gestor = GestorHorarios(self.periodo, [sin_equipo])
        with self.assertRaisesRegex(ValueError, "equipamiento"):
            gestor.crear_horario(1, self.asig, "LUNES", T(8), T(10), sin_equipo, "PRACTICA")
        self.assertEqual(sin_equipo.reservas, [])

    def test_docente_no_disponible_y_fuera_de_jornada(self):
        with self.assertRaisesRegex(ValueError, "disponible"):
            self.gestor.crear_horario(1, self.asig, "MARTES", T(8), T(10), self.a101, "TEORIA")
        self.d1.agregar_disponibilidad("LUNES", T(6), T(8))
        with self.assertRaisesRegex(ValueError, "jornada"):
            self.teoria(2, T(6), T(8))
        self.assertEqual(self.a101.reservas, [])

    def test_duracion_acumulada(self):
        self.teoria(1, T(8), T(9, 30))                   
        with self.assertRaisesRegex(ValueError, "horas de TEORIA"):
            self.teoria(2, T(10), T(11))                 
        self.assertEqual(len(self.asig.horarios), 1)
        self.teoria(3, T(10), T(10, 30))                  

    def test_id_repetido_y_aula_no_registrada(self):
        self.teoria(1)
        with self.assertRaises(ValueError):
            self.practica(1)
        ajena = Laboratorio("LX", 2, 1, True, "PCs")
        with self.assertRaisesRegex(ValueError, "registrada"):
            self.gestor.crear_horario(9, self.asig, "LUNES", T(10), T(12), ajena, "PRACTICA")

    def test_periodo_cerrado_bloquea(self):
        self.periodo.cerrar_periodo()
        with self.assertRaisesRegex(ValueError, "ABIERTO"):
            self.teoria(1)
        self.assertEqual(self.a101.reservas, [])

class TestModificarEliminar(BaseGestor):
    def test_modificar_a_aula_ocupada_conserva_reserva(self):
        self.escenario(("A", "MATUTINA"), ("B", "MATUTINA"))
        asig_a = self.asignar(1, nuevo_docente(), "A")
        asig_b = self.asignar(2, nuevo_docente(), "B")
        self.teoria(1, aula=self.a101, asig=asig_a)
        hb = self.teoria(2, aula=self.a103, asig=asig_b)
        antes = hb.datos()
        with self.assertRaisesRegex(ValueError, "ocupada"):
            self.gestor.modificar_horario(asig_b, hb, "LUNES", T(8), T(10), self.a101, "TEORIA")
        self.assertEqual(hb.datos(), antes)
        self.assertEqual(self.a103.reservas, [hb])
        self.assertEqual(len(self.a101.reservas), 1)

    def test_modificar_valido_mismo_objeto_y_reservas(self):
        h = self.teoria(1)
        ident = id(h)
        self.gestor.modificar_horario(self.asig, h, "LUNES", T(9), T(11), self.a103, "TEORIA")
        self.assertEqual(id(self.asig.horarios[0]), ident)
        self.assertEqual((h.hora_inicio, h.aula), (T(9), self.a103))
        self.assertEqual(self.a101.reservas, [])
        self.assertEqual(self.a103.reservas, [h])

    def test_modificar_puede_solaparse_consigo_mismo(self):
        h = self.teoria(1, T(8), T(10))
        self.gestor.modificar_horario(self.asig, h, "LUNES", T(9), T(11), self.a101, "TEORIA")
        self.assertEqual(h.hora_inicio, T(9))

    def test_rechazos_de_modificacion_dejan_todo_igual(self):
        t, p = self.teoria(1), self.practica(2)
        self.assertEqual(self.gestor.validar_planificacion(), [])
        with self.assertRaisesRegex(ValueError, "capacidad"):
            self.gestor.modificar_horario(self.asig, t, "LUNES", T(8), T(10), self.a102, "TEORIA")
        with self.assertRaisesRegex(ValueError, "no admite"):
            self.gestor.modificar_horario(self.asig, p, "LUNES", T(10), T(12), self.a101, "PRACTICA")
        self.assertIs(t.aula, self.a101)
        self.assertIs(p.aula, self.l101)
        self.assertEqual(self.a101.reservas, [t])
        self.assertEqual(self.l101.reservas, [p])
        self.assertEqual(self.a102.reservas, [])

    def test_eliminar_libera_aula(self):
        h = self.teoria(1)
        self.gestor.eliminar_horario(self.asig, h)
        self.assertEqual(self.a101.reservas, [])
        self.assertEqual(self.asig.horarios, [])
        self.teoria(2)                                      
        with self.assertRaises(ValueError):
            self.gestor.eliminar_horario(self.asig, h)      

    def test_modificar_y_eliminar_con_periodo_cerrado(self):
        h = self.teoria(1)
        self.periodo.cerrar_periodo()
        with self.assertRaises(ValueError):
            self.gestor.eliminar_horario(self.asig, h)
        with self.assertRaises(ValueError):
            self.gestor.modificar_horario(self.asig, h, "LUNES", T(9), T(11), self.a101, "TEORIA")
        self.assertEqual(self.a101.reservas, [h])

class TestValidarPlanificacion(BaseGestor):
    def test_plan_parcial_y_completo(self):
        self.teoria(1)
        problemas = self.gestor.validar_planificacion()
        self.assertEqual(len(problemas), 1)
        self.assertIn("PRACTICA", problemas[0])
        self.assertIn("120", problemas[0])
        self.practica(2)
        self.assertEqual(self.gestor.validar_planificacion(), [])

    def test_periodo_sin_paralelos(self):
        periodo = nuevo_periodo("2027-1")
        periodo.abrir_periodo()
        self.assertEqual(len(GestorHorarios(periodo, []).validar_planificacion()), 1)

    def test_paralelo_sin_asignaciones_y_materia_sin_docente(self):
        self.escenario(("A", "MATUTINA"), ("B", "MATUTINA"))
        self.asignar(1, nuevo_docente(), "A")
        self.assertTrue(any("B no tiene asignaciones" in p for p in self.gestor.validar_planificacion()))
        self.nivel.agregar_asignatura(Asignatura("MAT", "Matemática", 3, 1, 0))
        self.assertTrue(any("MAT" in p for p in self.gestor.validar_planificacion()))


class TestRecorridoCompleto(BaseGestor):
    def test_flujo_completo(self):
        t = self.teoria(1)
        p = self.practica(2)
        self.assertEqual(self.d1.ver_horario(self.periodo), [t, p])
        admin = Administrador(99, "Admin", "admin@correo.com")
        self.assertEqual(admin.ver_horario(self.periodo), [t, p])
        self.assertEqual(self.gestor.validar_planificacion(), [])

        self.gestor.modificar_horario(self.asig, t, "LUNES", T(8), T(9, 30), self.a101, "TEORIA")
        self.assertTrue(any("TEORIA" in x for x in self.gestor.validar_planificacion()))

        self.gestor.eliminar_horario(self.asig, p)
        self.assertEqual(self.l101.reservas, [])
        self.assertEqual(self.d1.ver_horario(self.periodo), [t])

if __name__ == "__main__":
    unittest.main()