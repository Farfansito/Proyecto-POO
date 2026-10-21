from datetime import time

DIAS = (
    "LUNES",
    "MARTES",
    "MIERCOLES",
    "JUEVES",
    "VIERNES",
)

JORNADAS = {
    "MATUTINA": (time(7, 0), time(13, 0)),
    "VESPERTINA": (time(13, 0), time(18, 0)),
    "NOCTURNA": (time(18, 0), time(22, 0)),
}

TIPOS_SESION = ("TEORIA", "PRACTICA")