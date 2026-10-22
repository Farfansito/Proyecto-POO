from modelos.aulas.aula import Aula


class Laboratorio(Aula):
    def __init__(self, codigo_aula, capacidad, piso, tiene_proyector, equipamiento: str):
        super().__init__(codigo_aula, capacidad, piso, tiene_proyector)
        if not isinstance(equipamiento, str):
            raise TypeError("equipamiento debe ser una cadena")
        if not equipamiento.strip():
            raise ValueError("equipamiento no puede estar vacío")
        self.equipamiento = equipamiento

    def tipo(self) -> str:
        return "LABORATORIO"

    def admite(self, tipo_sesion: str) -> bool:
        return tipo_sesion == "PRACTICA"

    def verificar_equipamiento(self) -> bool:
        """True si el texto de equipamiento contiene información."""
        return bool(self.equipamiento.strip())
