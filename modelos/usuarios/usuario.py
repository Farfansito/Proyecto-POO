from abc import ABC, abstractmethod
class Usuario(ABC):
    def __init__(self, id, nombre, correo):
        if not isinstance(id, int) or isinstance(id, bool) or id <= 0:
            raise ValueError("El ID debe ser un entero positivo.")
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if not isinstance(correo, str) or not correo.strip() or "@" not in correo or "." not in correo.split("@")[-1]:
            raise ValueError("El correo no tiene un formato básico válido.")

        self.id = id
        self.nombre = nombre.strip()
        self.correo = correo.strip()

    @abstractmethod
    def ver_horario(self, periodo):
        raise NotImplementedError
