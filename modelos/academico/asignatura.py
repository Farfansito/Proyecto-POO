"""Modelo de una asignatura."""

from .validaciones import entero, texto_no_vacio


class Asignatura:
    def __init__(self, codigo, nombre, creditos, horas_teoricas,
                 horas_practicas, descripcion=""):
        self._validar(codigo, nombre, creditos, horas_teoricas,
                      horas_practicas, descripcion)
        self.codigo = codigo.strip().upper()
        self.nombre = nombre.strip()
        self.creditos = creditos
        self.horas_teoricas = horas_teoricas
        self.horas_practicas = horas_practicas
        self.descripcion = descripcion

    @staticmethod
    def _validar(codigo, nombre, creditos, horas_teoricas,
                 horas_practicas, descripcion):
        texto_no_vacio(codigo, "El código")
        texto_no_vacio(nombre, "El nombre")
        entero(creditos, "Los créditos", 1)
        entero(horas_teoricas, "Las horas teóricas", 0)
        entero(horas_practicas, "Las horas prácticas", 0)
        if horas_teoricas + horas_practicas <= 0:
            raise ValueError("La suma de horas debe ser mayor que cero")
        if not isinstance(descripcion, str):
            raise ValueError("La descripción debe ser texto")

    def obtener_creditos(self):
        return self.creditos

    def actualizar_datos(self, nombre, creditos, horas_teoricas,
                         horas_practicas, descripcion):
        self._validar(self.codigo, nombre, creditos, horas_teoricas,
                      horas_practicas, descripcion)
        self.nombre = nombre.strip()
        self.creditos = creditos
        self.horas_teoricas = horas_teoricas
        self.horas_practicas = horas_practicas
        self.descripcion = descripcion
