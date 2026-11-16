"""Pruebas que demuestran cada principio SOLID aplicado al módulo de horarios."""
import unittest
from datetime import time as T

from modelos.horarios.horario import Horario
from pruebas.test_richard import BaseGestor
from servicios.reglas_bloque import ReglaBloque, reglas_estandar
from servicios.validador_bloques import ValidadorBloques


class TestResponsabilidadUnica(BaseGestor):
    """S: el validador decide si un bloque es válido; el gestor coordina cambios."""

    def candidato(self, id_=99, ini=T(8), fin=T(10)):
        return Horario(id_, "LUNES", ini, fin, self.a101, "TEORIA")

    def test_validador_funciona_sin_el_gestor(self):
        validador = ValidadorBloques(reglas_estandar([self.a101]))
        validador.validar(self.asig, self.candidato(), [self.asig])

    def test_validador_rechaza_cruce_sin_el_gestor(self):
        self.teoria(1, T(8), T(10))
        validador = ValidadorBloques(reglas_estandar([self.a101]))
        with self.assertRaisesRegex(ValueError, "Cruce de horario"):
            validador.validar(self.asig, self.candidato(98, T(9), T(11)), [self.asig])

    def test_validar_no_modifica_datos(self):
        validador = ValidadorBloques(reglas_estandar([self.a101]))
        validador.validar(self.asig, self.candidato(), [self.asig])
        self.assertEqual(self.a101.reservas, [])
        self.assertEqual(self.asig.horarios, [])


class NoViernes(ReglaBloque):
    """Regla nueva, definida fuera del validador y de las reglas estándar."""

    def verificar(self, contexto):
        if contexto.candidato.dia == "VIERNES":
            raise ValueError("No se programan clases los viernes.")


class TestAbiertoCerrado(BaseGestor):
    """O: una regla nueva se añade sin modificar ValidadorBloques."""

    def test_regla_nueva_se_incorpora_sin_tocar_el_validador(self):
        self.d1.agregar_disponibilidad("VIERNES", T(8), T(12))
        validador = ValidadorBloques(reglas_estandar([self.a101]))
        viernes = Horario(97, "VIERNES", T(8), T(10), self.a101, "TEORIA")
        validador.validar(self.asig, viernes, [self.asig])  # las reglas estándar lo aceptan
        validador = ValidadorBloques(reglas_estandar([self.a101]) + [NoViernes()])
        with self.assertRaisesRegex(ValueError, "viernes"):
            validador.validar(self.asig, viernes, [self.asig])

    def test_sin_la_regla_nueva_el_comportamiento_no_cambia(self):
        validador = ValidadorBloques(reglas_estandar([self.a101]))
        lunes = Horario(96, "LUNES", T(8), T(10), self.a101, "TEORIA")
        validador.validar(self.asig, lunes, [self.asig])

    def test_el_orden_de_reglas_se_conserva(self):
        nombres = [type(r).__name__ for r in reglas_estandar([])]
        self.assertEqual(nombres[:3], ["AulaRegistrada", "DentroDeJornada", "CapacidadDelAula"])
        self.assertEqual(nombres[-1], "HorasPermitidas")


if __name__ == "__main__":
    unittest.main()