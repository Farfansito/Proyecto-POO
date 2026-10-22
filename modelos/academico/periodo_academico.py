"""Modelo del periodo académico y sus transiciones de estado."""

from datetime import date

from .validaciones import texto_no_vacio


class PeriodoAcademico:
    PLANIFICADO = "PLANIFICADO"
    ABIERTO = "ABIERTO"
    CERRADO = "CERRADO"

    def __init__(self, codigo, nombre, fecha_inicio, fecha_fin):
        texto_no_vacio(codigo, "El código")
        texto_no_vacio(nombre, "El nombre")
        if not isinstance(fecha_inicio, date) or not isinstance(fecha_fin, date):
            raise ValueError("Las fechas deben ser objetos date")
        if fecha_inicio > fecha_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha fin")
        self.codigo = codigo.strip()
        self.nombre = nombre.strip()
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = self.PLANIFICADO
        self._paralelos = []

    def abrir_periodo(self):
        if self.estado != self.PLANIFICADO:
            raise ValueError("Solo se puede abrir un periodo planificado")
        self.estado = self.ABIERTO

    def cerrar_periodo(self):
        if self.estado != self.ABIERTO:
            raise ValueError("Solo se puede cerrar un periodo abierto")
        self.estado = self.CERRADO

    def esta_vigente(self):
        return self.estado == self.ABIERTO

    def agregar_paralelo(self, paralelo):
        from .paralelo import Paralelo

        if self.estado != self.PLANIFICADO:
            raise ValueError("Solo se agregan paralelos a un periodo planificado")
        if not isinstance(paralelo, Paralelo) or paralelo.periodo is not self:
            raise ValueError("El paralelo debe pertenecer a este periodo")
        if paralelo not in self._paralelos:
            self._paralelos.append(paralelo)

    def paralelos(self):
        return self._paralelos.copy()
