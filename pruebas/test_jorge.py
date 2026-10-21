import unittest
from types import SimpleNamespace

from aplicacion import SistemaSCHOS


class TestSistemaSCHOS(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaSCHOS()

    def test_ids_independientes(self):
        self.assertEqual(self.sistema.nuevo_id("usuario"), 1)
        self.assertEqual(self.sistema.nuevo_id("usuario"), 2)
        self.assertEqual(self.sistema.nuevo_id("horario"), 1)

    def test_entidad_invalida(self):
        with self.assertRaises(ValueError):
            self.sistema.nuevo_id("inventado")

        self.assertEqual(self.sistema.nuevo_id("usuario"), 1)

    def test_usuario_duplicado(self):
        usuario = SimpleNamespace(
            id=1, nombre="Jorge", correo="jorge@correo.com"
        )
        self.sistema.registrar_usuario(usuario)

        with self.assertRaises(ValueError):
            self.sistema.registrar_usuario(usuario)

        self.assertEqual(len(self.sistema.usuarios), 1)
        self.assertIs(self.sistema.usuarios[1], usuario)

    def test_correo_duplicado(self):
        primero = SimpleNamespace(
            id=1, nombre="Jorge", correo="jorge@correo.com"
        )
        segundo = SimpleNamespace(
            id=2, nombre="Otro", correo=" JORGE@correo.com "
        )
        self.sistema.registrar_usuario(primero)

        with self.assertRaises(ValueError):
            self.sistema.registrar_usuario(segundo)

        self.assertEqual(len(self.sistema.usuarios), 1)
        self.assertNotIn(2, self.sistema.usuarios)

    def test_aula_duplicada(self):
        primera = SimpleNamespace(codigo_aula="A101")
        segunda = SimpleNamespace(codigo_aula=" a101 ")
        self.sistema.registrar_aula(primera)

        with self.assertRaises(ValueError):
            self.sistema.registrar_aula(segunda)

        self.assertEqual(len(self.sistema.aulas), 1)
        self.assertIs(self.sistema.aulas["A101"], primera)

    def test_asignatura_duplicada(self):
        primera = SimpleNamespace(codigo="POO")
        segunda = SimpleNamespace(codigo=" poo ")
        self.sistema.registrar_asignatura(primera)

        with self.assertRaises(ValueError):
            self.sistema.registrar_asignatura(segunda)

        self.assertEqual(len(self.sistema.asignaturas), 1)
        self.assertIs(self.sistema.asignaturas["POO"], primera)

    def test_nivel_duplicado(self):
        primero = SimpleNamespace(numero=1)
        segundo = SimpleNamespace(numero=1)
        self.sistema.registrar_nivel(primero)

        with self.assertRaises(ValueError):
            self.sistema.registrar_nivel(segundo)

        self.assertEqual(len(self.sistema.niveles), 1)
        self.assertIs(self.sistema.niveles[1], primero)

    def test_periodo_no_se_reemplaza(self):
        primero = SimpleNamespace(codigo="2026-1")
        segundo = SimpleNamespace(codigo="2026-2")
        self.sistema.establecer_periodo(primero)

        with self.assertRaises(ValueError):
            self.sistema.establecer_periodo(segundo)

        self.assertIs(self.sistema.periodo, primero)