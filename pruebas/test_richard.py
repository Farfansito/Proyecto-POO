"""Pruebas de Richard: Horario, AsignacionAcademica y GestorHorarios.

Los módulos de Kevin (Paralelo, Nivel, Periodo), Aníbal (Aula) y Tanya (Docente) todavía
no están integrados, así que aquí se usan dobles mínimos que siguen EXACTAMENTE los
contratos de la guía. Cuando sus ramas estén en main, se pueden reemplazar por las
clases reales cambiando solo la sección "Dobles".
Ejecutar desde la raíz:  py -m unittest discover -s pruebas -v
"""
import unittest
from datetime import time

from modelos.academico.asignacion_academica import AsignacionAcademica
from modelos.horarios.horario import Horario
from servicios.gestor_horarios import GestorHorarios


# ============================== Dobles (contratos de la guía) ==============================
class AulaDoble:
    def __init__(self, codigo_aula, capacidad, tipos, equipamiento=True):
        self.codigo_aula, self.capacidad = codigo_aula, capacidad
        self._tipos, self._equip, self._reservas = tipos, equipamiento, []

    def admite(self, tipo_sesion):
        return tipo_sesion in self._tipos

    def verificar_equipamiento(self):
        return self._equip

    def verificar_disponibilidad(self, horario, ignorar=None):
        return not any(r is not ignorar and r.detectar_conflicto(horario) for r in self._reservas)

    def reservar(self, horario):
        if horario.aula is not self:
            raise ValueError("El horario no pertenece a esta aula.")
        if not self.verificar_disponibilidad(horario):
            raise ValueError("Aula ocupada.")
        self._reservas.append(horario)

    def liberar(self, horario):
        for i, r in enumerate(self._reservas):
            if r is horario:
                del self._reservas[i]
                return
        raise ValueError("La reserva no existe.")

    @property
    def reservas(self):
        return list(self._reservas)


def teorica(cod, cap):
    return AulaDoble(cod, cap, ("TEORIA",))


def laboratorio(cod, cap, equip=True):
    return AulaDoble(cod, cap, ("PRACTICA",), equip)


class AsignaturaDoble:
    def __init__(self, codigo, ht, hp):
        self.codigo, self.horas_teoricas, self.horas_practicas = codigo, ht, hp


class NivelDoble:
    def __init__(self, numero, asignaturas):
        self.numero, self._asig = numero, list(asignaturas)

    def obtener_asignaturas(self):
        return list(self._asig)


class PeriodoDoble:
    def __init__(self, estado="ABIERTO"):
        self.estado, self._paralelos = estado, []

    @property
    def paralelos(self):
        return list(self._paralelos)


class ParaleloDoble:
    def __init__(self, codigo, jornada, cupo, nivel, periodo):
        self.codigo, self.jornada, self.cupo_maximo = codigo, jornada, cupo
        self.nivel, self.periodo, self._asig = nivel, periodo, []
        periodo._paralelos.append(self)

    @property
    def asignaciones(self):
        return list(self._asig)

    def agregar_asignacion(self, a):
        if a.paralelo is not self:
            raise ValueError("La asignación es de otro paralelo.")
        if any(x.asignatura.codigo == a.asignatura.codigo for x in self._asig):
            raise ValueError("Materia repetida en el paralelo.")
        self._asig.append(a)


class DocenteDoble:
    def __init__(self, nombre, max_horas, disponibilidad):
        self.nombre, self.max_horas_semanales = nombre, max_horas
        self._disp, self._asig = disponibilidad, []   # [(dia, inicio, fin)]

    def esta_disponible(self, dia, inicio, fin):
        return any(d == dia and i <= inicio and fin <= f for d, i, f in self._disp)

    def horas_asignadas(self, periodo):
        return sum(a.horas_semanales for a in self._asig if a.paralelo.periodo is periodo)

    def asignar_asignatura(self, a):
        if a.docente is not self or any(x is a for x in self._asig):
            raise ValueError("Asignación inválida o duplicada.")
        if self.horas_asignadas(a.paralelo.periodo) + a.horas_semanales > self.max_horas_semanales:
            raise ValueError("Supera el máximo del docente.")
        self._asig.append(a)

    def quitar_asignacion(self, a):
        if not any(x is a for x in self._asig):
            raise ValueError("No existe la asignación.")
        self._asig = [x for x in self._asig if x is not a]

    @property
    def asignaciones(self):
        return list(self._asig)


T = time
LUN_8_12 = [("LUNES", T(8, 0), T(12, 0))]


# ======================================= Horario =======================================
class TestHorario(unittest.TestCase):
    def setUp(self):
        self.aula = teorica("A101", 2)

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


# =============================== AsignacionAcademica ===================================
class TestAsignacion(unittest.TestCase):
    def setUp(self):
        per = PeriodoDoble()
        poo = AsignaturaDoble("POO", 2, 2)
        par = ParaleloDoble("A", "MATUTINA", 2, NivelDoble(1, [poo]), per)
        self.doc = DocenteDoble("D1", 4, LUN_8_12)
        self.asig = AsignacionAcademica(1, self.doc, poo, par)
        self.aula = teorica("A101", 2)

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
            AsignacionAcademica(0, self.doc, self.asig.asignatura, self.asig.paralelo)


# ================================== GestorHorarios =====================================
class BaseGestor(unittest.TestCase):
    def setUp(self):
        self.periodo = PeriodoDoble()
        self.poo = AsignaturaDoble("POO", 2, 2)
        self.nivel = NivelDoble(1, [self.poo])
        self.par_a = ParaleloDoble("A", "MATUTINA", 2, self.nivel, self.periodo)
        self.a101 = teorica("A101", 2)
        self.l101 = laboratorio("L101", 2)
        self.a102 = teorica("A102", 1)
        self.a103 = teorica("A103", 2)
        self.gestor = GestorHorarios(self.periodo, [self.a101, self.l101, self.a102, self.a103])
        self.d1 = DocenteDoble("D1", 4, LUN_8_12)
        self.asig = self.gestor.crear_asignacion(1, self.d1, self.poo, self.par_a)

    def teoria(self, id_, ini=T(8), fin=T(10), aula=None, asig=None):
        return self.gestor.crear_horario(id_, asig or self.asig, "LUNES", ini, fin, aula or self.a101, "TEORIA")

    def practica(self, id_, ini=T(10), fin=T(12), aula=None):
        return self.gestor.crear_horario(id_, self.asig, "LUNES", ini, fin, aula or self.l101, "PRACTICA")

    def segundo_paralelo(self, codigo="B", docente=None, jornada="MATUTINA"):
        par = ParaleloDoble(codigo, jornada, 2, self.nivel, self.periodo)
        doc = docente or DocenteDoble("D2", 4, LUN_8_12)
        asig = self.gestor.crear_asignacion(10 + len(self.periodo.paralelos), doc, self.poo, par)
        return par, doc, asig


class TestCrearAsignacion(BaseGestor):
    def test_se_registra_en_docente_y_paralelo(self):
        self.assertIn(self.asig, self.d1.asignaciones)
        self.assertIn(self.asig, self.par_a.asignaciones)

    def test_carga_docente_excedida_no_agrega_nada(self):
        par = ParaleloDoble("B", "MATUTINA", 2, self.nivel, self.periodo)
        with self.assertRaises(ValueError):
            self.gestor.crear_asignacion(2, self.d1, self.poo, par)   # 4 + 4 > 4
        self.assertEqual(par.asignaciones, [])
        self.assertEqual(len(self.d1.asignaciones), 1)

    def test_rechazos(self):
        otra = AsignaturaDoble("MAT", 1, 0)
        ajeno = ParaleloDoble("Z", "MATUTINA", 2, self.nivel, PeriodoDoble())
        casos = [
            (2, self.d1, self.poo, self.par_a),     # materia repetida en el paralelo
            (2, self.d1, otra, self.par_a),         # materia no es del nivel
            (2, self.d1, self.poo, ajeno),          # paralelo de otro periodo
            (1, self.d1, self.poo, self.par_a),     # ID repetido
        ]
        for c in casos:
            with self.subTest(c[0], materia=c[2].codigo), self.assertRaises(ValueError):
                self.gestor.crear_asignacion(*c)
        self.assertEqual(len(self.par_a.asignaciones), 1)


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
            self.practica(2, T(9), T(11))                # cruza con la teoría (docente/paralelo)
        self.assertEqual(self.l101.reservas, [])
        self.assertEqual(len(self.asig.horarios), 1)

    def test_aula_compartida_docentes_distintos(self):
        self.teoria(1)
        par, doc, asig_b = self.segundo_paralelo()
        with self.assertRaisesRegex(ValueError, "ocupada"):
            self.teoria(2, aula=self.a101, asig=asig_b)
        self.assertEqual(asig_b.horarios, [])

    def test_docente_compartido_aulas_distintas(self):
        doc = DocenteDoble("D3", 8, LUN_8_12)
        self.gestor.crear_asignacion(5, doc, self.poo, ParaleloDoble("C", "MATUTINA", 2, self.nivel, self.periodo))
        par_d = ParaleloDoble("D", "MATUTINA", 2, self.nivel, self.periodo)
        asig_c = [a for p in self.periodo.paralelos for a in p.asignaciones if a.id_asignacion == 5][0]
        asig_d = self.gestor.crear_asignacion(6, doc, self.poo, par_d)
        self.teoria(1, aula=self.a101, asig=asig_c)
        with self.assertRaisesRegex(ValueError, "docente"):
            self.teoria(2, aula=self.a103, asig=asig_d)
        self.assertEqual(self.a103.reservas, [])

    def test_mismo_paralelo_recursos_distintos(self):
        mat = AsignaturaDoble("MAT", 2, 0)
        self.nivel._asig.append(mat)
        d2 = DocenteDoble("D2", 4, LUN_8_12)
        asig_m = self.gestor.crear_asignacion(2, d2, mat, self.par_a)
        self.teoria(1, aula=self.a101)
        with self.assertRaisesRegex(ValueError, "paralelo"):
            self.teoria(2, aula=self.a103, asig=asig_m)
        self.assertEqual(self.a103.reservas, [])

    def test_paralelos_distintos_recursos_distintos_pueden_coincidir(self):
        self.teoria(1)
        _, _, asig_b = self.segundo_paralelo()
        self.teoria(2, aula=self.a103, asig=asig_b)       # mismo horario, nada compartido
        self.assertEqual(len(asig_b.horarios), 1)

    def test_jornada_y_tipo(self):
        par_n, doc, asig_n = self.segundo_paralelo("N", DocenteDoble("DN", 4, [("LUNES", T(7), T(12))]), "NOCTURNA")
        with self.assertRaisesRegex(ValueError, "jornada"):
            self.teoria(1, T(7), T(9), asig=asig_n)
        with self.assertRaisesRegex(ValueError, "no admite"):
            self.gestor.crear_horario(2, self.asig, "LUNES", T(8), T(10), self.a101, "PRACTICA")

    def test_capacidad_y_equipamiento(self):
        with self.assertRaisesRegex(ValueError, "capacidad"):
            self.teoria(1, aula=self.a102)
        sin_equipo = laboratorio("L102", 2, equip=False)
        g = GestorHorarios(self.periodo, [sin_equipo])
        with self.assertRaisesRegex(ValueError, "equipamiento"):
            g.crear_horario(1, self.asig, "LUNES", T(8), T(10), sin_equipo, "PRACTICA")

    def test_docente_no_disponible(self):
        with self.assertRaisesRegex(ValueError, "disponible"):
            self.gestor.crear_horario(1, self.asig, "MARTES", T(8), T(10), self.a101, "TEORIA")

    def test_duracion_acumulada(self):
        self.teoria(1, T(8), T(9, 30))                    # 90 min, quedan 30
        with self.assertRaisesRegex(ValueError, "horas de TEORIA"):
            self.teoria(2, T(10), T(11))                  # 60 > 30
        self.assertEqual(len(self.asig.horarios), 1)
        self.teoria(3, T(10), T(10, 30))                  # 30 sí cabe

    def test_id_repetido_y_aula_no_registrada(self):
        self.teoria(1)
        with self.assertRaises(ValueError):
            self.practica(1)
        ajena = laboratorio("LX", 2)
        with self.assertRaisesRegex(ValueError, "registrada"):
            self.gestor.crear_horario(9, self.asig, "LUNES", T(10), T(12), ajena, "PRACTICA")

    def test_periodo_cerrado_bloquea(self):
        self.periodo.estado = "CERRADO"
        with self.assertRaisesRegex(ValueError, "ABIERTO"):
            self.teoria(1)
        self.assertEqual(self.a101.reservas, [])


class TestModificarEliminar(BaseGestor):
    def test_modificar_a_aula_ocupada_conserva_reserva(self):
        _, _, asig_b = self.segundo_paralelo()
        self.teoria(1, aula=self.a101)
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

    def test_demo_pasos_4_y_5(self):
        t, p = self.teoria(1), self.practica(2)
        self.assertEqual(self.gestor.validar_planificacion(), [])
        with self.assertRaisesRegex(ValueError, "capacidad"):
            self.gestor.modificar_horario(self.asig, t, "LUNES", T(8), T(10), self.a102, "TEORIA")
        with self.assertRaisesRegex(ValueError, "no admite"):
            self.gestor.modificar_horario(self.asig, p, "LUNES", T(10), T(12), self.a101, "PRACTICA")
        self.assertIs(t.aula, self.a101)
        self.assertIs(p.aula, self.l101)
        self.assertEqual(self.l101.reservas, [p])

    def test_eliminar_libera_aula(self):
        h = self.teoria(1)
        self.gestor.eliminar_horario(self.asig, h)
        self.assertEqual(self.a101.reservas, [])
        self.assertEqual(self.asig.horarios, [])
        self.teoria(2)                                      # la franja se puede reutilizar
        with self.assertRaises(ValueError):
            self.gestor.eliminar_horario(self.asig, h)      # ya no existe

    def test_modificar_y_eliminar_con_periodo_cerrado(self):
        h = self.teoria(1)
        self.periodo.estado = "CERRADO"
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
        vacio = GestorHorarios(PeriodoDoble(), [])
        self.assertEqual(len(vacio.validar_planificacion()), 1)

    def test_paralelo_sin_asignaciones_y_materia_sin_docente(self):
        ParaleloDoble("B", "MATUTINA", 2, self.nivel, self.periodo)
        self.assertTrue(any("B no tiene asignaciones" in p for p in self.gestor.validar_planificacion()))
        self.nivel._asig.append(AsignaturaDoble("MAT", 1, 0))
        self.assertTrue(any("MAT" in p for p in self.gestor.validar_planificacion()))


if __name__ == "__main__":
    unittest.main()