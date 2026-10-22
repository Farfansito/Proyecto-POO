import unittest
from datetime import date
from types import SimpleNamespace

from modelos.academico.asignatura import Asignatura
from modelos.academico.nivel import Nivel
from modelos.academico.paralelo import Paralelo
from modelos.academico.periodo_academico import PeriodoAcademico


class TestCatalogoAcademico(unittest.TestCase):
    def setUp(self):
        self.asignatura = Asignatura("POO", "Programación", 3, 2, 2)
        self.nivel = Nivel(1, "Primero")
        self.periodo = PeriodoAcademico(
            "2026A", "Periodo 2026", date(2026, 1, 1), date(2026, 6, 30)
        )

    def test_rechaza_nivel_fuera_de_rango(self):
        for numero in (0, 10):
            with self.subTest(numero=numero), self.assertRaises(ValueError):
                Nivel(numero, "Nivel")

    def test_rechaza_horas_negativas_sin_cambiar_datos(self):
        with self.assertRaises(ValueError):
            self.asignatura.actualizar_datos("Nuevo", 4, -1, 2, "desc")
        self.assertEqual(self.asignatura.nombre, "Programación")
        self.assertEqual(self.asignatura.creditos, 3)

    def test_rechaza_fechas_invertidas(self):
        with self.assertRaises(ValueError):
            PeriodoAcademico("X", "Inválido", date(2026, 2, 1), date(2026, 1, 1))

    def test_rechaza_asignatura_duplicada_y_devuelve_copia(self):
        self.nivel.agregar_asignatura(self.asignatura)
        with self.assertRaises(ValueError):
            self.nivel.agregar_asignatura(Asignatura(" poo ", "Otra", 2, 1, 1))
        lista = self.nivel.obtener_asignaturas()
        lista.clear()
        self.assertEqual(len(self.nivel.obtener_asignaturas()), 1)

    def test_cupo_uno_rechaza_el_segundo_y_al_borrar_libera_cupo(self):
        paralelo = Paralelo("A", "Matutina", 1, self.nivel, self.periodo)
        paralelo.agregar_estudiante("Kevin")
        self.assertFalse(paralelo.verificar_cupo())
        with self.assertRaises(ValueError):
            paralelo.agregar_estudiante("Ana")
        paralelo.quitar_estudiante("Kevin")
        self.assertTrue(paralelo.verificar_cupo())
        paralelo.agregar_estudiante("Ana")
        self.assertEqual(paralelo.numero_estudiantes, 1)

    def test_rechaza_estudiante_duplicado_y_quitar_no_inscrito(self):
        paralelo = Paralelo("A", "Matutina", 2, self.nivel, self.periodo)
        paralelo.agregar_estudiante("Kevin")
        with self.assertRaises(ValueError):
            paralelo.agregar_estudiante("Kevin")
        with self.assertRaises(ValueError):
            paralelo.quitar_estudiante("Ana")

    def test_agrega_paralelo_solo_al_periodo_que_le_corresponde(self):
        paralelo = Paralelo("A", "Matutina", 2, self.nivel, self.periodo)
        self.periodo.agregar_paralelo(paralelo)
        self.assertEqual(self.periodo.paralelos(), [paralelo])
        self.assertEqual(self.nivel._paralelos, [paralelo])
        self.periodo.abrir_periodo()
        with self.assertRaises(ValueError):
            self.periodo.agregar_paralelo(paralelo)

    def test_asignacion_debe_pertenecer_al_nivel_y_no_repetirse(self):
        paralelo = Paralelo("A", "Matutina", 2, self.nivel, self.periodo)
        with self.assertRaises(ValueError):
            paralelo.agregar_asignacion(SimpleNamespace(
                asignatura=self.asignatura, paralelo=paralelo
            ))
        self.nivel.agregar_asignatura(self.asignatura)
        asignacion = SimpleNamespace(asignatura=self.asignatura, paralelo=paralelo)
        paralelo.agregar_asignacion(asignacion)
        with self.assertRaises(ValueError):
            paralelo.agregar_asignacion(asignacion)
        copia = paralelo.asignaciones
        copia.clear()
        self.assertEqual(paralelo.asignaciones, [asignacion])

    def test_rechaza_asignacion_de_otro_paralelo(self):
        self.nivel.agregar_asignatura(self.asignatura)
        paralelo = Paralelo("A", "Matutina", 2, self.nivel, self.periodo)
        otro = Paralelo("B", "Vespertina", 2, self.nivel, self.periodo)
        with self.assertRaises(ValueError):
            paralelo.agregar_asignacion(SimpleNamespace(
                asignatura=self.asignatura, paralelo=otro
            ))

    def test_transiciones_del_periodo(self):
        with self.assertRaises(ValueError):
            self.periodo.cerrar_periodo()
        self.periodo.abrir_periodo()
        self.assertTrue(self.periodo.esta_vigente())
        self.periodo.cerrar_periodo()
        self.assertFalse(self.periodo.esta_vigente())


if __name__ == "__main__":
    unittest.main()
