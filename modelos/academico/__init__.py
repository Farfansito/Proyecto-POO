"""Modelos del catálogo académico de SCHOS."""

from datetime import date


def _texto_no_vacio(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} debe ser un texto no vacío")


def _entero(valor, campo, minimo):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < minimo:
        raise ValueError(f"{campo} debe ser un entero mayor o igual a {minimo}")


class Asignatura:
    def __init__(self, codigo, nombre, creditos, horas_teoricas,
                 horas_practicas, descripcion=""):
        self._validar(codigo, nombre, creditos, horas_teoricas,
                      horas_practicas, descripcion)
        self.codigo = codigo.strip()
        self.nombre = nombre.strip()
        self.creditos = creditos
        self.horas_teoricas = horas_teoricas
        self.horas_practicas = horas_practicas
        self.descripcion = descripcion

    @staticmethod
    def _validar(codigo, nombre, creditos, horas_teoricas,
                 horas_practicas, descripcion):
        _texto_no_vacio(codigo, "El código")
        _texto_no_vacio(nombre, "El nombre")
        _entero(creditos, "Los créditos", 1)
        _entero(horas_teoricas, "Las horas teóricas", 0)
        _entero(horas_practicas, "Las horas prácticas", 0)
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


class Nivel:
    def __init__(self, numero, nombre):
        _entero(numero, "El número de nivel", 1)
        if numero > 9:
            raise ValueError("El número de nivel debe estar entre 1 y 9")
        _texto_no_vacio(nombre, "El nombre")
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


class PeriodoAcademico:
    PLANIFICADO = "PLANIFICADO"
    ABIERTO = "ABIERTO"
    CERRADO = "CERRADO"

    def __init__(self, codigo, nombre, fecha_inicio, fecha_fin):
        _texto_no_vacio(codigo, "El código")
        _texto_no_vacio(nombre, "El nombre")
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
        if self.estado != self.PLANIFICADO:
            raise ValueError("Solo se agregan paralelos a un periodo planificado")
        if not isinstance(paralelo, Paralelo) or paralelo.periodo is not self:
            raise ValueError("El paralelo debe pertenecer a este periodo")
        if paralelo not in self._paralelos:
            self._paralelos.append(paralelo)

    def paralelos(self):
        return self._paralelos.copy()


class Paralelo:
    def __init__(self, codigo, jornada, cupo_maximo, nivel, periodo):
        _texto_no_vacio(codigo, "El código")
        _texto_no_vacio(jornada, "La jornada")
        _entero(cupo_maximo, "El cupo máximo", 1)
        if not isinstance(nivel, Nivel):
            raise ValueError("Se requiere un nivel válido")
        if not isinstance(periodo, PeriodoAcademico):
            raise ValueError("Se requiere un periodo académico válido")
        self.codigo = codigo.strip()
        self.jornada = jornada.strip()
        self.cupo_maximo = cupo_maximo
        self.nivel = nivel
        self.periodo = periodo
        self._estudiantes = []
        self._asignaciones = []
        nivel._paralelos.append(self)

    @property
    def numero_estudiantes(self):
        return len(self._estudiantes)

    def verificar_cupo(self):
        return self.numero_estudiantes < self.cupo_maximo

    def agregar_estudiante(self, estudiante):
        if any(e == estudiante for e in self._estudiantes):
            raise ValueError("El estudiante ya está inscrito en este paralelo")
        if not self.verificar_cupo():
            raise ValueError("El paralelo no tiene cupos disponibles")
        self._estudiantes.append(estudiante)

    def quitar_estudiante(self, estudiante):
        for indice, inscrito in enumerate(self._estudiantes):
            if inscrito == estudiante:
                del self._estudiantes[indice]
                return
        raise ValueError("El estudiante no está inscrito en este paralelo")

    def agregar_asignacion(self, asignacion):
        asignatura = getattr(asignacion, "asignatura", None)
        if getattr(asignacion, "paralelo", None) is not self:
            raise ValueError("La asignación debe pertenecer a este paralelo")
        if not isinstance(asignatura, Asignatura):
            raise ValueError("La asignación debe referirse a una asignatura")
        if not any(a.codigo.casefold() == asignatura.codigo.casefold()
                   for a in self.nivel._asignaturas):
            raise ValueError("La asignatura no pertenece al nivel del paralelo")
        if any(getattr(a, "asignatura", a).codigo.casefold() ==
               asignatura.codigo.casefold() for a in self._asignaciones):
            raise ValueError("La asignatura ya está asignada a este paralelo")
        self._asignaciones.append(asignacion)

    @property
    def asignaciones(self):
        return self._asignaciones.copy()

    @property
    def estudiantes(self):
        return self._estudiantes.copy()


__all__ = ["Asignatura", "Nivel", "PeriodoAcademico", "Paralelo"]
