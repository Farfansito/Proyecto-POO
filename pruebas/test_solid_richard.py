"""Pruebas que demuestran cada principio SOLID aplicado al módulo de horarios."""
import unittest
from datetime import time as T

from modelos.horarios.horario import Horario
from pruebas.test_richard import BaseGestor
from servicios.validador_bloques import ValidadorBloques


class TestResponsabilidadUnica(BaseGestor):
    """S: el validador decide si un bloque es válido; el gestor coordina cambios."""

    def candidato(self, id_=99, ini=T(8), fin=T(10)):
        return Horario(id_, "LUNES", ini, fin, self.a101, "TEORIA")

    def test_validador_funciona_sin_el_gestor(self):
        validador = ValidadorBloques([self.a101])
        validador.validar(self.asig, self.candidato(), [self.asig])

    def test_validador_rechaza_cruce_sin_el_gestor(self):
        self.teoria(1, T(8), T(10))
        validador = ValidadorBloques([self.a101])
        with self.assertRaisesRegex(ValueError, "Cruce de horario"):
            validador.validar(self.asig, self.candidato(98, T(9), T(11)), [self.asig])

    def test_validar_no_modifica_datos(self):
        validador = ValidadorBloques([self.a101])
        validador.validar(self.asig, self.candidato(), [self.asig])
        self.assertEqual(self.a101.reservas, [])
        self.assertEqual(self.asig.horarios, [])


if __name__ == "__main__":
    unittest.main()