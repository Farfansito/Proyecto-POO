from modelos.aulas.aula import Aula


class Auditorio(Aula):
    def __init__(self, codigo_aula, capacidad, piso, tiene_proyector, tiene_sonido: bool):
        super().__init__(codigo_aula, capacidad, piso, tiene_proyector)
        self.tiene_sonido = self._validar_bool(tiene_sonido, "tiene_sonido")

    def tipo(self) -> str:
        return "AUDITORIO"