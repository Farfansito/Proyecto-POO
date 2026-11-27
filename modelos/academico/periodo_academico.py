"""Modelo del periodo académico y sus transiciones de estado."""

from datetime import date, datetime

from .validaciones import texto_no_vacio


class PeriodoAcademico:
    PLANIFICADO = "PLANIFICADO"
    ABIERTO = "ABIERTO"
    CERRADO = "CERRADO"

    def __init__(self, codigo, nombre, fecha_inicio, fecha_fin):
        texto_no_vacio(codigo, "El código")
        texto_no_vacio(nombre, "El nombre")
        if (
            not isinstance(fecha_inicio, date)
            or isinstance(fecha_inicio, datetime)
            or not isinstance(fecha_fin, date)
            or isinstance(fecha_fin, datetime)
        ):
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
        hoy = date.today()
        return self.fecha_inicio <= hoy <= self.fecha_fin

    def buscar_paralelo(self, codigo):
        """Busca por código y devuelve la instancia registrada o None."""
        texto_no_vacio(codigo, "El código de paralelo")
        codigo_normalizado = codigo.strip().casefold()
        return next(
            (p for p in self._paralelos if p.codigo.casefold() == codigo_normalizado),
            None,
        )

    def agregar_paralelo(self, paralelo):
        from .paralelo import Paralelo

        if self.estado != self.ABIERTO:
            raise ValueError("Solo se agregan paralelos a un periodo abierto")
        if not isinstance(paralelo, Paralelo) or paralelo.periodo is not self:
            raise ValueError("El paralelo debe pertenecer a este periodo")
        if self.buscar_paralelo(paralelo.codigo) is not None:
            raise ValueError("Ya existe un paralelo con ese código")
        self._paralelos.append(paralelo)

    @property
    def paralelos(self):
        return self._paralelos.copy()
