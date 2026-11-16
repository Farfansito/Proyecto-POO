from modelos.aulas.aula_teorica import AulaTeorica
from modelos.aulas.creadores.creador_aula import CreadorAula


class CreadorAulaTeorica(CreadorAula):
    clave = "TEORICA"
    nombre = "Aula teórica"

    def crear_aula(self, codigo_aula, capacidad, piso, tiene_proyector, **extras) -> AulaTeorica:
        self._extras_requeridos(extras)
        return AulaTeorica(codigo_aula, capacidad, piso, tiene_proyector)
