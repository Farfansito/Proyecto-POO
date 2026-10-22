"""Modelo de nivel académico."""

from .asignatura import Asignatura
from .validaciones import entero, texto_no_vacio


class Nivel:
    def __init__(self, numero, nombre):
        entero(numero, "El número de nivel", 1)
        if numero > 9:
            raise ValueError("El número de nivel debe estar entre 1 y 9")
        texto_no_vacio(nombre, "El nombre")
        self.numero = numero
        self.nombre = nombre.strip()
        self._asignaturas = []
        self._paralelos = []

    def agregar_asignatura(self, asignatura):
        if not isinstance(asignatura, Asignatura):
            raise ValueError("Se requiere una asignatura válida")
        if any(a.codigo.casefold() == asignatura.codigo.casefold()
               for a in self._asignaturas):
            raise ValueError("Ya existe una asignatura con ese código")
        self._asignaturas.append(asignatura)

    def obtener_asignaturas(self):
        return self._asignaturas.copy()
