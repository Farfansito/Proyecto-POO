import unittest
from datetime import time

from modelos.aulas.aula import Aula
from modelos.aulas.aula_teorica import AulaTeorica
from modelos.aulas.auditorio import Auditorio
from modelos.aulas.laboratorio import Laboratorio
from modelos.aulas.sala_sustentacion import SalaSustentacion
from modelos.horarios.disponibilidad_docente import DisponibilidadDocente
from modelos.horarios.horario import Horario


def bloque(aula, ini, fin, dia="LUNES"):
    return Horario(dia, time(ini), time(fin), aula)


class TestAula(unittest.TestCase):
    def setUp(self):
        self.aula = AulaTeorica("A-101", 40, 1, True)

    def test_aula_abstracta(self):
        with self.assertRaises(TypeError):
            Aula("X", 10, 0, False)

    def test_atributos_y_reservas_vacias(self):
        a = self.aula
        self.assertEqual((a.codigo_aula, a.capacidad, a.piso, a.tiene_proyector), ("A-101", 40, 1, True))
        self.assertEqual(a.reservas, [])
        self.assertFalse(hasattr(a, "laboratorio"))

    def test_validaciones(self):
        with self.assertRaises(ValueError):
            AulaTeorica("A", 0, 1, True)
        with self.assertRaises(ValueError):
            AulaTeorica("A", -5, 1, True)
        with self.assertRaises(TypeError):
            AulaTeorica("A", 10.5, 1, True)
        with self.assertRaises(ValueError):
            AulaTeorica("A", 10, -1, True)
        with self.assertRaises(TypeError):
            AulaTeorica("A", 10, 1.0, True)
        with self.assertRaises(ValueError):
            AulaTeorica("  ", 10, 1, True)
        with self.assertRaises(TypeError):
            AulaTeorica("A", 10, 1, "si")
        with self.assertRaises(TypeError):
            Auditorio("AU", 100, 0, True, 1)
        with self.assertRaises(TypeError):
            SalaSustentacion("S", 10, 0, True, None)

    def test_tipos_y_admite(self):
        casos = [
            (AulaTeorica("A", 10, 0, True), "TEORICA", True, False),
            (Laboratorio("L", 10, 0, True, "PCs"), "LABORATORIO", False, True),
            (Auditorio("AU", 10, 0, True, True), "AUDITORIO", False, False),
            (SalaSustentacion("S", 10, 0, True, False), "SUSTENTACION", False, False),
        ]
        for aula, tipo, teoria, practica in casos:
            self.assertEqual(aula.tipo(), tipo)
            self.assertEqual(aula.admite("TEORIA"), teoria)
            self.assertEqual(aula.admite("PRACTICA"), practica)

    def test_laboratorio_equipamiento(self):
        lab = Laboratorio("L", 10, 0, True, "20 PCs")
        self.assertTrue(lab.verificar_equipamiento())
        self.assertEqual(lab.equipamiento, "20 PCs")
        with self.assertRaises(ValueError):
            Laboratorio("L", 10, 0, True, "   ")
        with self.assertRaises(TypeError):
            Laboratorio("L", 10, 0, True, None)

    def test_atributos_propios(self):
        self.assertTrue(Auditorio("AU", 10, 0, True, True).tiene_sonido)
        self.assertFalse(SalaSustentacion("S", 10, 0, True, False).tiene_grabacion)

    def test_reservar_cruce_y_contiguo(self):
        a = self.aula
        a.reservar(bloque(a, 8, 10))
        with self.assertRaises(ValueError):
            a.reservar(bloque(a, 9, 11))
        a.reservar(bloque(a, 10, 11))
        self.assertEqual(len(a.reservas), 2)

    def test_mismo_bloque_y_otro_dia(self):
        a = self.aula
        h = bloque(a, 8, 10)
        a.reservar(h)
        with self.assertRaises(ValueError):
            a.reservar(h)
        with self.assertRaises(ValueError):
            a.reservar(bloque(a, 8, 10))
        a.reservar(bloque(a, 8, 10, "MARTES"))
        self.assertEqual(len(a.reservas), 2)

    def test_reservar_exige_aula_propia(self):
        otra = AulaTeorica("A-102", 40, 1, True)
        with self.assertRaises(ValueError):
            self.aula.reservar(bloque(otra, 8, 10))
        with self.assertRaises(ValueError):
            self.aula.reservar(Horario("LUNES", time(8), time(10)))

    def test_liberar_reutiliza_franja(self):
        a = self.aula
        h = bloque(a, 8, 10)
        a.reservar(h)
        a.liberar(h)
        a.reservar(bloque(a, 9, 11))

    def test_liberar_inexistente(self):
        with self.assertRaises(ValueError):
            self.aula.liberar(bloque(self.aula, 8, 10))

    def test_reservas_es_copia(self):
        a = self.aula
        a.reservar(bloque(a, 8, 10))
        a.reservas.clear()
        self.assertEqual(len(a.reservas), 1)

    def test_modificacion_ignora_solo_su_reserva(self):
        a = self.aula
        h1, h2 = bloque(a, 8, 10), bloque(a, 11, 12)
        a.reservar(h1)
        a.reservar(h2)
        propuesta = bloque(a, 9, 10)
        self.assertFalse(a.verificar_disponibilidad(propuesta))
        self.assertTrue(a.verificar_disponibilidad(propuesta, ignorar=h1))
        cruza_otra = bloque(a, 10, 12)
        self.assertFalse(a.verificar_disponibilidad(cruza_otra, ignorar=h1))
        self.assertEqual(len(a.reservas), 2)  # no se quitó la reserva anterior


class TestDisponibilidad(unittest.TestCase):
    def test_normaliza_dia(self):
        d = DisponibilidadDocente(" Miércoles ", time(8), time(12))
        self.assertEqual(d.dia, "MIERCOLES")
        self.assertEqual((d.hora_inicio, d.hora_fin), (time(8), time(12)))

    def test_intervalos_invalidos(self):
        with self.assertRaises(ValueError):
            DisponibilidadDocente("LUNES", time(12), time(8))
        with self.assertRaises(ValueError):
            DisponibilidadDocente("LUNES", time(8), time(8))
        with self.assertRaises(ValueError):
            DisponibilidadDocente("FERIADO", time(8), time(9))
        with self.assertRaises(TypeError):
            DisponibilidadDocente("LUNES", "08:00", time(9))

    def test_cubre(self):
        d = DisponibilidadDocente("LUNES", time(8), time(12))
        self.assertTrue(d.cubre("lunes", time(8), time(12)))
        self.assertTrue(d.cubre("LUNES", time(9), time(10)))
        self.assertFalse(d.cubre("LUNES", time(7), time(9)))
        self.assertFalse(d.cubre("LUNES", time(11), time(13)))
        self.assertFalse(d.cubre("MARTES", time(9), time(10)))
        self.assertFalse(d.cubre("LUNES", time(10), time(9)))   # intervalo inválido
        self.assertFalse(d.cubre("LUNES", time(9), time(9)))
        self.assertFalse(d.cubre("XYZ", time(9), time(10)))


if __name__ == "__main__":
    unittest.main()
