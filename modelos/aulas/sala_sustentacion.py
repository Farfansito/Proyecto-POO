from modelos.aulas.aula import Aula


class SalaSustentacion(Aula):
    def __init__(self, codigo_aula, capacidad, piso, tiene_proyector, tiene_grabacion: bool):
        super().__init__(codigo_aula, capacidad, piso, tiene_proyector)
        self.tiene_grabacion = self._validar_bool(tiene_grabacion, "tiene_grabacion")

    def tipo(self) -> str:
        return "SUSTENTACION"
