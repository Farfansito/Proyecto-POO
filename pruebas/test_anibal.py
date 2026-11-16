"""Pruebas del patrón Factory Method para aulas (responsabilidad de Aníbal)."""
import ast
import io
import pathlib
import unittest
from contextlib import redirect_stdout
from datetime import time
from unittest.mock import patch

import main as programa
from aplicacion import SistemaSCHOS
from menu_aulas import menu_aulas
from modelos.aulas.aula import Aula
from modelos.aulas.aula_teorica import AulaTeorica
from modelos.aulas.auditorio import Auditorio
from modelos.aulas.laboratorio import Laboratorio
from modelos.aulas.sala_sustentacion import SalaSustentacion
from modelos.aulas.creadores.catalogo_creadores import CatalogoCreadores, crear_catalogo_por_defecto
from modelos.aulas.creadores.creador_aula import CampoAula, CreadorAula
from modelos.aulas.creadores.creador_aula_teorica import CreadorAulaTeorica
from modelos.aulas.creadores.creador_auditorio import CreadorAuditorio
from modelos.aulas.creadores.creador_laboratorio import CreadorLaboratorio
from modelos.aulas.creadores.creador_sala_sustentacion import CreadorSalaSustentacion
from modelos.horarios.horario import Horario
from servicios.registro_aulas import ServicioRegistroAulas

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# (creador, clase esperada, tipo(), extras, atributo propio, valor)
CASOS = [
    (CreadorAulaTeorica, AulaTeorica, "TEORICA", {}, None, None),
    (CreadorLaboratorio, Laboratorio, "LABORATORIO", {"equipamiento": "20 PCs"}, "equipamiento", "20 PCs"),
    (CreadorAuditorio, Auditorio, "AUDITORIO", {"tiene_sonido": True}, "tiene_sonido", True),
    (CreadorSalaSustentacion, SalaSustentacion, "SUSTENTACION", {"tiene_grabacion": False}, "tiene_grabacion", False),
]


def importaciones(nombre_archivo):
    arbol = ast.parse((RAIZ / nombre_archivo).read_text(encoding="utf-8"))
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module)
        elif isinstance(nodo, ast.Import):
            modulos.update(a.name for a in nodo.names)
    return modulos


class TestCreadoresConcretos(unittest.TestCase):
    def test_creador_abstracto_no_se_instancia(self):
        with self.assertRaises(TypeError):
            CreadorAula()

    def test_cada_creador_genera_su_tipo(self):
        for creador_cls, clase, tipo, extras, attr, valor in CASOS:
            with self.subTest(tipo=tipo):
                creador = creador_cls()
                aula = creador.crear_aula("X-1", 30, 2, True, **extras)
                self.assertIs(type(aula), clase)
                self.assertEqual(aula.tipo(), tipo)
                self.assertEqual(creador.clave, tipo)
                self.assertEqual((aula.codigo_aula, aula.capacidad, aula.piso, aula.tiene_proyector),
                                 ("X-1", 30, 2, True))
                if attr:
                    self.assertEqual(getattr(aula, attr), valor)

    def test_cada_llamada_crea_un_objeto_nuevo(self):
        creador = CreadorAulaTeorica()
        self.assertIsNot(creador.crear_aula("A", 10, 0, True), creador.crear_aula("A", 10, 0, True))

    def test_faltan_o_sobran_datos(self):
        with self.assertRaises(ValueError):
            CreadorLaboratorio().crear_aula("L", 10, 0, True)
        with self.assertRaises(ValueError):
            CreadorAulaTeorica().crear_aula("A", 10, 0, True, equipamiento="x")
        with self.assertRaises(ValueError):
            CreadorAuditorio().crear_aula("AU", 10, 0, True, tiene_sonido=True, extra=1)

    def test_las_validaciones_del_producto_se_mantienen(self):
        with self.assertRaises(ValueError):
            CreadorAulaTeorica().crear_aula("A", 0, 0, True)
        with self.assertRaises(TypeError):
            CreadorAuditorio().crear_aula("AU", 10, 0, True, tiene_sonido=1)
        with self.assertRaises(ValueError):
            CreadorLaboratorio().crear_aula("L", 10, 0, True, equipamiento="  ")

    def test_campo_aula_tipo_invalido(self):
        with self.assertRaises(ValueError):
            CampoAula("x", "X", "fecha")


class TestCatalogo(unittest.TestCase):
    def test_catalogo_por_defecto_tiene_los_cuatro_tipos(self):
        claves = [c.clave for c in crear_catalogo_por_defecto().listar()]
        self.assertEqual(claves, ["TEORICA", "LABORATORIO", "AUDITORIO", "SUSTENTACION"])

    def test_obtener_normaliza_y_rechaza_desconocidos(self):
        cat = crear_catalogo_por_defecto()
        self.assertIsInstance(cat.obtener(" laboratorio "), CreadorLaboratorio)
        with self.assertRaises(ValueError):
            cat.obtener("PISCINA")

    def test_rechaza_duplicados_y_no_creadores(self):
        cat = CatalogoCreadores()
        cat.registrar(CreadorAulaTeorica())
        with self.assertRaises(ValueError):
            cat.registrar(CreadorAulaTeorica())
        with self.assertRaises(TypeError):
            cat.registrar(object())


class TestServicioRegistro(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaSCHOS()
        self.servicio = ServicioRegistroAulas(self.sistema, crear_catalogo_por_defecto())

    def test_registra_y_recupera_los_cuatro_tipos(self):
        for creador_cls, clase, tipo, extras, _, _ in CASOS:
            aula = self.servicio.registrar_aula(tipo, f"{tipo[:3]}-1", 25, 1, True, **extras)
            self.assertIs(type(aula), clase)
            self.assertIs(self.sistema.aulas[f"{tipo[:3]}-1"], aula)
        self.assertEqual(len(self.sistema.aulas), 4)
        self.assertEqual([a.tipo() for a in self.servicio.consultar_aulas()],
                         ["TEORICA", "LABORATORIO", "AUDITORIO", "SUSTENTACION"])

    def test_codigo_duplicado_no_altera_el_registro(self):
        original = self.servicio.registrar_aula("TEORICA", "A-1", 20, 0, True)
        with self.assertRaises(ValueError):
            self.servicio.registrar_aula("AUDITORIO", "a-1", 90, 0, True, tiene_sonido=True)
        self.assertEqual(len(self.sistema.aulas), 1)
        self.assertIs(self.sistema.aulas["A-1"], original)

    def test_datos_invalidos_no_registran_nada(self):
        with self.assertRaises(ValueError):
            self.servicio.registrar_aula("LABORATORIO", "L-1", 10, 0, True, equipamiento="")
        with self.assertRaises(ValueError):
            self.servicio.registrar_aula("PISCINA", "P-1", 10, 0, True)
        self.assertEqual(self.sistema.aulas, {})

    def test_campos_adicionales_por_tipo(self):
        self.assertEqual(self.servicio.campos_adicionales("TEORICA"), ())
        self.assertEqual([c.nombre for c in self.servicio.campos_adicionales("LABORATORIO")], ["equipamiento"])

    def test_aulas_creadas_sirven_en_el_resto_del_sistema(self):
        lab = self.servicio.registrar_aula("LABORATORIO", "L-1", 20, 0, True, equipamiento="PCs")
        teo = self.servicio.registrar_aula("TEORICA", "T-1", 40, 1, True)
        h1 = Horario(1, "LUNES", time(8), time(10), lab, "PRACTICA")
        h2 = Horario(2, "LUNES", time(8), time(10), teo, "TEORIA")
        lab.reservar(h1)
        teo.reservar(h2)
        self.assertEqual(lab.reservas, [h1])
        self.assertFalse(lab.verificar_disponibilidad(Horario(3, "LUNES", time(9), time(11), lab, "PRACTICA")))


class TestSolid(unittest.TestCase):
    def test_srp_creadores_no_dependen_de_persistencia_ni_interfaz(self):
        for archivo in ("creador_aula", "creador_aula_teorica", "creador_laboratorio",
                        "creador_auditorio", "creador_sala_sustentacion", "catalogo_creadores"):
            mods = importaciones(f"modelos/aulas/creadores/{archivo}.py")
            for prohibido in ("aplicacion", "main", "menu_aulas", "servicios.registro_aulas"):
                self.assertNotIn(prohibido, mods, f"{archivo} importa {prohibido}")

    def test_srp_servicio_y_menu_no_mezclan_responsabilidades(self):
        self.assertNotIn("menu_aulas", importaciones("servicios/registro_aulas.py"))
        self.assertNotIn("aplicacion", importaciones("menu_aulas.py"))

    def test_ocp_un_tipo_nuevo_se_agrega_sin_tocar_codigo_existente(self):
        class Biblioteca(Aula):
            def tipo(self):
                return "BIBLIOTECA"

        class CreadorBiblioteca(CreadorAula):
            clave = "BIBLIOTECA"
            nombre = "Biblioteca"

            def crear_aula(self, codigo_aula, capacidad, piso, tiene_proyector, **extras):
                self._extras_requeridos(extras)
                return Biblioteca(codigo_aula, capacidad, piso, tiene_proyector)

        catalogo = crear_catalogo_por_defecto()
        catalogo.registrar(CreadorBiblioteca())
        sistema = SistemaSCHOS()
        aula = ServicioRegistroAulas(sistema, catalogo).registrar_aula("BIBLIOTECA", "B-1", 60, 0, False)
        self.assertEqual(aula.tipo(), "BIBLIOTECA")
        self.assertIn("B-1", sistema.aulas)

    def test_lsp_toda_aula_creada_cumple_el_contrato_de_aula(self):
        for creador_cls, _, tipo, extras, _, _ in CASOS:
            with self.subTest(tipo=tipo):
                aula = creador_cls().crear_aula("Z-1", 10, 0, True, **extras)
                self.assertIsInstance(aula, Aula)
                self.assertIsInstance(aula.tipo(), str)
                self.assertIsInstance(aula.admite("TEORIA"), bool)
                self.assertIsInstance(aula.admite("PRACTICA"), bool)
                h = Horario(1, "MARTES", time(8), time(9), aula, "TEORIA")
                aula.reservar(h)
                self.assertEqual(aula.reservas, [h])
                aula.liberar(h)
                self.assertEqual(aula.reservas, [])
                self.assertEqual(str(aula), f"{tipo}[Z-1]")

    def test_isp_contrato_del_creador_es_minimo(self):
        self.assertEqual(CreadorAula.__abstractmethods__, {"clave", "nombre", "crear_aula"})
        publicos = {n for n in vars(CreadorAula) if not n.startswith("_")}
        self.assertEqual(publicos, {"clave", "nombre", "crear_aula", "campos_adicionales"})

    def test_dip_servicio_y_menu_no_importan_clases_concretas(self):
        concretos = {"modelos.aulas.aula_teorica", "modelos.aulas.laboratorio",
                     "modelos.aulas.auditorio", "modelos.aulas.sala_sustentacion",
                     "modelos.aulas.creadores.creador_aula_teorica",
                     "modelos.aulas.creadores.creador_laboratorio",
                     "modelos.aulas.creadores.creador_auditorio",
                     "modelos.aulas.creadores.creador_sala_sustentacion"}
        for archivo in ("servicios/registro_aulas.py", "menu_aulas.py"):
            self.assertFalse(importaciones(archivo) & concretos, archivo)

    def test_dip_servicio_funciona_con_dobles_inyectados(self):
        class AlmacenFalso:
            def __init__(self):
                self.aulas, self.recibidas = {}, []

            def registrar_aula(self, aula):
                self.recibidas.append(aula)

        class CreadorFalso(CreadorAula):
            clave, nombre = "FALSA", "Falsa"

            def crear_aula(self, *a, **k):
                return "aula-falsa"

        catalogo = CatalogoCreadores()
        catalogo.registrar(CreadorFalso())
        almacen = AlmacenFalso()
        self.assertEqual(ServicioRegistroAulas(almacen, catalogo).registrar_aula("FALSA", "F", 1, 0, True), "aula-falsa")
        self.assertEqual(almacen.recibidas, ["aula-falsa"])


def ejecutar_menu(entradas, sistema=None):
    sistema = sistema or SistemaSCHOS()
    servicio = ServicioRegistroAulas(sistema, crear_catalogo_por_defecto())
    salida = io.StringIO()
    with patch("builtins.input", side_effect=entradas), redirect_stdout(salida):
        menu_aulas(servicio, programa.leer_entero)
    return sistema, salida.getvalue()


ENTRADAS_CUATRO_TIPOS = [
    "1", "1", "a-101", "40", "1", "s",          # teórica
    "1", "2", "l-1", "20", "0", "n", "20 PCs",  # laboratorio
    "1", "3", "au-1", "200", "0", "s", "s",     # auditorio
    "1", "4", "s-1", "15", "2", "n", "n",       # sala de sustentación
]


class TestMenuYMain(unittest.TestCase):
    def test_menu_crea_los_cuatro_tipos_y_los_consulta(self):
        sistema, salida = ejecutar_menu(ENTRADAS_CUATRO_TIPOS + ["2", "0"])
        self.assertEqual({k: type(v) for k, v in sistema.aulas.items()},
                         {"A-101": AulaTeorica, "L-1": Laboratorio, "AU-1": Auditorio, "S-1": SalaSustentacion})
        self.assertTrue(sistema.aulas["AU-1"].tiene_sonido)
        self.assertFalse(sistema.aulas["S-1"].tiene_grabacion)
        self.assertEqual(sistema.aulas["L-1"].equipamiento, "20 PCs")
        self.assertIn("A-101 | Tipo: TEORICA | Capacidad: 40 | Piso: 1", salida)
        self.assertIn("S-1 | Tipo: SUSTENTACION | Capacidad: 15 | Piso: 2", salida)

    def test_menu_tipo_invalido_y_codigo_duplicado(self):
        sistema, salida = ejecutar_menu([
            "1", "9",                                   # tipo fuera de rango
            "1", "1", "a-1", "10", "0", "s",            # ok
            "1", "1", "A-1", "10", "0", "s",            # duplicado
            "0"])
        self.assertIn("Tipo de aula no válido.", salida)
        self.assertIn("Ya existe un aula con ese código.", salida)
        self.assertEqual(len(sistema.aulas), 1)

    def test_menu_dato_propio_invalido_se_informa(self):
        sistema, salida = ejecutar_menu(["1", "2", "L-2", "10", "0", "s", "   ", "0"])
        self.assertIn("equipamiento no puede estar vacío", salida)
        self.assertEqual(sistema.aulas, {})

    def test_main_opcion_2_registra_aulas_y_resumen_las_cuenta(self):
        entradas = ["2"] + ENTRADAS_CUATRO_TIPOS + ["0", "5", "0"]
        salida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), redirect_stdout(salida):
            programa.main()
        self.assertIn("Aulas: 4", salida.getvalue())

    def test_main_conserva_opciones_existentes(self):
        entradas = ["1", "4", "1", "Nivel uno", "0", "5", "3", "0"]
        salida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), redirect_stdout(salida):
            programa.main()
        texto = salida.getvalue()
        self.assertIn("Nivel registrado correctamente.", texto)
        self.assertIn("Niveles: 1", texto)
        self.assertIn("todavía está pendiente", texto)


if __name__ == "__main__":
    unittest.main()
