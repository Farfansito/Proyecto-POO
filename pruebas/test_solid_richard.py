"""Pruebas que demuestran cada principio SOLID aplicado al módulo de horarios."""
import unittest
from datetime import time as T

from modelos.aulas.aula import Aula
from modelos.aulas.aula_teorica import AulaTeorica
from modelos.aulas.auditorio import Auditorio
from modelos.aulas.laboratorio import Laboratorio
from modelos.aulas.sala_sustentacion import SalaSustentacion
from modelos.horarios.horario import Horario
from pruebas.test_richard import BaseGestor
from servicios.contratos import AuditorPlanificacion, EditorPlanificacion, VerificadorBloques
from servicios.gestor_horarios import GestorHorarios
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


class AulaTaller(Aula):
    """Subtipo nuevo que admite práctica y no redefine verificar_equipamiento."""

    def tipo(self) -> str:
        return "TALLER"

    def admite(self, tipo_sesion: str) -> bool:
        return tipo_sesion == "PRACTICA"


class TestSustitucionLiskov(BaseGestor):
    """L: el validador acepta cualquier subtipo de Aula sin preguntar cuál es."""

    def aulas(self):
        return [
            AulaTeorica("T1", 2, 1, True),
            Laboratorio("LAB1", 2, 1, True, "10 PCs"),
            Auditorio("AUD1", 2, 1, True, True),
            SalaSustentacion("SUS1", 2, 1, True, False),
            AulaTaller("TAL1", 2, 1, True),
        ]

    def test_ningun_subtipo_rompe_el_validador(self):
        aulas = self.aulas()
        validador = ValidadorBloques(reglas_estandar(aulas))
        for aula in aulas:
            for tipo in ("TEORIA", "PRACTICA"):
                with self.subTest(aula=str(aula), tipo=tipo):
                    candidato = Horario(95, "LUNES", T(8), T(10), aula, tipo)
                    if aula.admite(tipo):
                        validador.validar(self.asig, candidato, [self.asig])
                    else:
                        with self.assertRaisesRegex(ValueError, "no admite"):
                            validador.validar(self.asig, candidato, [self.asig])

    def test_todo_aula_cumple_el_contrato_de_equipamiento(self):
        for aula in self.aulas():
            with self.subTest(aula=str(aula)):
                self.assertIsInstance(aula.verificar_equipamiento(), bool)

    def test_laboratorio_sin_equipo_sigue_rechazandose(self):
        lab = Laboratorio("LAB2", 2, 1, True, "PCs")
        lab.equipamiento = ""
        validador = ValidadorBloques(reglas_estandar([lab]))
        candidato = Horario(94, "LUNES", T(8), T(10), lab, "PRACTICA")
        with self.assertRaisesRegex(ValueError, "equipamiento"):
            validador.validar(self.asig, candidato, [self.asig])

class AuditorMinimo(AuditorPlanificacion):
    """Cliente que solo revisa: no tiene por qué implementar operaciones de edición."""

    def validar_planificacion(self):
        return ["pendiente"]


class TestSegregacionInterfaces(BaseGestor):
    """I: contratos pequeños; nadie implementa operaciones que no necesita."""

    def test_un_auditor_no_exige_metodos_de_edicion(self):
        self.assertEqual(AuditorMinimo().validar_planificacion(), ["pendiente"])
        self.assertFalse(hasattr(AuditorMinimo(), "crear_horario"))

    def test_un_contrato_incompleto_no_se_puede_instanciar(self):
        class EditorIncompleto(EditorPlanificacion):
            def crear_horario(self, *args): ...

        with self.assertRaises(TypeError):
            EditorIncompleto()

    def test_el_gestor_cumple_los_dos_contratos_de_cliente(self):
        self.assertIsInstance(self.gestor, EditorPlanificacion)
        self.assertIsInstance(self.gestor, AuditorPlanificacion)
        self.assertNotIsInstance(self.gestor, VerificadorBloques)

    def test_el_validador_solo_verifica(self):
        validador = ValidadorBloques([])
        self.assertIsInstance(validador, VerificadorBloques)
        self.assertNotIsInstance(validador, EditorPlanificacion)
        self.assertNotIsInstance(validador, AuditorPlanificacion)

class VerificadorQueAcepta(VerificadorBloques):
    def __init__(self):
        self.llamadas = []

    def validar(self, asignacion, candidato, asignaciones, original=None):
        self.llamadas.append(candidato.id_horario)


class VerificadorQueRechaza(VerificadorBloques):
    def validar(self, asignacion, candidato, asignaciones, original=None):
        raise ValueError("rechazado por el verificador de prueba")


class TestInversionDependencias(BaseGestor):
    """D: el gestor depende del contrato VerificadorBloques y se le inyecta uno."""

    def gestor_con(self, verificador):
        return GestorHorarios(self.periodo, [self.a101, self.l101], verificador)

    def test_el_gestor_usa_el_verificador_inyectado(self):
        verificador = VerificadorQueAcepta()
        gestor = self.gestor_con(verificador)
        gestor.crear_horario(1, self.asig, "LUNES", T(8), T(10), self.a101, "TEORIA")
        self.assertEqual(verificador.llamadas, [1])

    def test_un_verificador_que_rechaza_no_deja_reservas(self):
        gestor = self.gestor_con(VerificadorQueRechaza())
        with self.assertRaisesRegex(ValueError, "verificador de prueba"):
            gestor.crear_horario(1, self.asig, "LUNES", T(8), T(10), self.a101, "TEORIA")
        self.assertEqual(self.a101.reservas, [])
        self.assertEqual(self.asig.horarios, [])

    def test_las_reglas_ya_no_estan_dentro_del_gestor(self):
        # Con un verificador permisivo, un bloque fuera de jornada se acepta:
        # prueba de que esa regla vive en el verificador y no en el gestor.
        gestor = self.gestor_con(VerificadorQueAcepta())
        h = gestor.crear_horario(1, self.asig, "LUNES", T(15), T(17), self.a101, "TEORIA")
        self.assertEqual(h.hora_inicio, T(15))

    def test_sin_inyeccion_se_usan_las_reglas_estandar(self):
        with self.assertRaisesRegex(ValueError, "jornada"):
            self.gestor.crear_horario(1, self.asig, "LUNES", T(15), T(17), self.a101, "TEORIA")
                   
if __name__ == "__main__":
    unittest.main()