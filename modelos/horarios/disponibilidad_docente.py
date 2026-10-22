import unicodedata
from datetime import time

DIAS_VALIDOS = ("LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO")


def normalizar_dia(dia: str) -> str:
    """Quita espacios y tildes y pasa a mayúsculas ('Miércoles' -> 'MIERCOLES')."""
    if not isinstance(dia, str):
        raise TypeError("dia debe ser una cadena")
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", dia.strip())
                         if unicodedata.category(c) != "Mn")
    normal = sin_tildes.upper()
    if normal not in DIAS_VALIDOS:
        raise ValueError(f"día inválido: {dia!r}")
    return normal


def _validar_intervalo(inicio, fin) -> None:
    if not isinstance(inicio, time) or not isinstance(fin, time):
        raise TypeError("las horas deben ser datetime.time")
    if inicio >= fin:
        raise ValueError("hora_inicio debe ser anterior a hora_fin")


class DisponibilidadDocente:
    def __init__(self, dia: str, hora_inicio: time, hora_fin: time):
        self.dia = normalizar_dia(dia)
        _validar_intervalo(hora_inicio, hora_fin)
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

    def cubre(self, dia: str, inicio: time, fin: time) -> bool:
        """True solo si [inicio, fin] es válido y cabe completo en este día."""
        try:
            dia = normalizar_dia(dia)
            _validar_intervalo(inicio, fin)
        except (TypeError, ValueError):
            return False
        return (dia == self.dia
                and inicio >= self.hora_inicio and fin <= self.hora_fin)