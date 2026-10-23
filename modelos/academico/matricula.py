from datetime import date


class Matricula:
    def __init__(self, id_matricula, estudiante, periodo):
        if type(id_matricula) != int or id_matricula <= 0:
            raise ValueError("El id de la matrícula debe ser un entero positivo.")
        self.id_matricula = id_matricula
        self.estudiante = estudiante
        self.periodo = periodo
        self.fecha = date.today()
        self.estado = "PENDIENTE"
        self.paralelo = None

    def agregar_paralelo(self, paralelo):
        if self.estado != "PENDIENTE":
            raise ValueError("Solo se puede elegir paralelo en una matrícula pendiente.")
        if self.periodo.estado != "ABIERTO":
            raise ValueError("El periodo no está abierto.")
        if paralelo.periodo is not self.periodo:
            raise ValueError("El paralelo es de otro periodo.")
        if paralelo not in self.periodo.paralelos():
            raise ValueError("El paralelo no está registrado en el periodo.")
        self.paralelo = paralelo  # todavía no ocupa cupo

    def confirmar(self):
        if self.periodo.estado != "ABIERTO":
            raise ValueError("El periodo no está abierto.")
        if self.estado != "PENDIENTE":
            raise ValueError("Solo se puede confirmar una matrícula pendiente.")
        if self.paralelo is None:
            raise ValueError("Primero hay que elegir un paralelo.")
        if not self.paralelo.verificar_cupo():
            raise ValueError("El paralelo no tiene cupos disponibles.")
        if self.estudiante in self.paralelo.estudiantes:
            raise ValueError("El estudiante ya está inscrito en ese paralelo.")
        self.paralelo.agregar_estudiante(self.estudiante)
        self.estado = "CONFIRMADA"

    def cancelar(self):
        if self.periodo.estado != "ABIERTO":
            raise ValueError("El periodo no está abierto.")
        if self.estado == "CANCELADA":
            raise ValueError("La matrícula ya está cancelada.")
        if self.estado == "CONFIRMADA":
            self.paralelo.quitar_estudiante(self.estudiante)  # libera el cupo
        self.estado = "CANCELADA"