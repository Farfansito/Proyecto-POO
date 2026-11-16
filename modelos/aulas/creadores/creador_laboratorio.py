from modelos.aulas.creadores.creador_aula import CampoAula, CreadorAula
from modelos.aulas.laboratorio import Laboratorio


class CreadorLaboratorio(CreadorAula):
    clave = "LABORATORIO"
    nombre = "Laboratorio"

    def campos_adicionales(self) -> tuple[CampoAula, ...]:
        return (CampoAula("equipamiento", "Equipamiento del laboratorio", "texto"),)

    def crear_aula(self, codigo_aula, capacidad, piso, tiene_proyector, **extras) -> Laboratorio:
        extras = self._extras_requeridos(extras)
        return Laboratorio(codigo_aula, capacidad, piso, tiene_proyector,
                           extras["equipamiento"])
