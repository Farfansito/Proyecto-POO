from datetime import time


class Horario:

    duracion_maxima_min = 180

    def __init__(self, dia: str, hora_inicio: time, hora_fin: time, aula: str):
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.aula = aula

    def calcularDuracion(self):
        return 120

    def validarDisponibilidad(self, otro_horario):
        return self.dia != otro_horario.dia

    @classmethod
    def cambiar_duracion_maxima(cls, nueva_duracion):
        cls.duracion_maxima_min = nueva_duracion

    @staticmethod
    def es_hora_valida(hora):
        return isinstance(hora, time)


class Paralelo:

    cupo_estandar = 30

    def __init__(self, codigo, jornada, cupo_maximo):
        self.codigo = codigo
        self.jornada = jornada
        self.cupo_maximo = cupo_maximo
        self.numero_estudiantes = 0

    def verificarCupo(self):
        return self.numero_estudiantes < self.cupo_maximo

    def agregarEstudiante(self, cantidad):
        if self.verificarCupo():
            self.numero_estudiantes += cantidad

    @staticmethod
    def es_jornada_valida(jornada):
        return jornada.lower() in ["matutina", "vespertina", "nocturna"]

    @classmethod
    def cambiar_cupo_estandar(cls, nuevo_cupo):
        cls.cupo_estandar = nuevo_cupo


class Asignatura:

    creditos_maximos = 6

    def __init__(self, codigo, nombre, creditos):
        self.codigo = codigo
        self.nombre = nombre
        self.creditos = creditos

    def obtenerCreditos(self):
        return self.creditos

    def actualizarDatos(self, nuevo_nombre):
        self.nombre = nuevo_nombre

    @classmethod
    def cambiar_creditos_maximos(cls, nuevos_creditos):
        cls.creditos_maximos = nuevos_creditos

    @staticmethod
    def es_codigo_valido(codigo):
        return len(codigo) >= 3


class Docente:

    carga_maxima = 4

    def __init__(self, id_docente, nombre, especialidad):
        self.id_docente = id_docente
        self.nombre = nombre
        self.especialidad = especialidad
        self.asignaturas = []

    def consultarHorario(self):
        return f"Horario asignado al docente {self.nombre}"

    def asignarAsignatura(self, asignatura):
        if len(self.asignaturas) < Docente.carga_maxima:
            self.asignaturas.append(asignatura)

    @classmethod
    def cambiar_carga_maxima(cls, nueva_carga):
        cls.carga_maxima = nueva_carga

    @staticmethod
    def es_id_valido(id_docente):
        return str(id_docente).startswith("D")


class Estudiante:

    max_matriculas = 5

    def __init__(self, id_estudiante, nombre, correo):
        self.id_estudiante = id_estudiante
        self.nombre = nombre
        self.correo = correo
        self.paralelos = []

    def solicitar_matricula(self):
        print(f"El estudiante {self.nombre} solicitó matrícula.")

    def matricular(self, paralelo):
        if len(self.paralelos) < Estudiante.max_matriculas:
            self.paralelos.append(paralelo)

    def ver_horario(self):
        print(f"Mostrando horario de {self.nombre}")

    @classmethod
    def cambiar_max_matriculas(cls, nuevo_max):
        cls.max_matriculas = nuevo_max

    @staticmethod
    def es_correo_valido(correo):
        return "@" in correo and "." in correo

class AyudandeCatedra (Estudiante, Docente):

    def __init__ (self, id_estudiante, id_docente, nombre, correo):
        Estudiante.__init__(self, id_estudiante, nombre, correo)
        Docente.__init__(self, id_docente, nombre, "")


if __name__ == "__main__":

    horario1 = Horario("Lunes", time(8, 0), time(10, 0), "Aula 101")
    horario2 = Horario("Martes", time(10, 0), time(12, 0), "Aula 102")
    print(f"Duración del horario 1: {horario1.calcularDuracion()} minutos")
    print(f"Duración del horario 2: {horario2.calcularDuracion()} minutos")

    paralelo1 = Paralelo("P001", "Matutina", 30)
    paralelo2 = Paralelo("P002", "Vespertina", 25)
    print(f"Verificando cupo del paralelo 1: {paralelo1.verificarCupo()}")
    print(f"Verificando cupo del paralelo 2: {paralelo2.verificarCupo()}")

    asignatura1 = Asignatura("AS001", "Matemáticas", 4)
    asignatura2 = Asignatura("AS002", "Física", 3)
    print(f"Créditos de la asignatura 1: {asignatura1.obtenerCreditos()}")
    print(f"Créditos de la asignatura 2: {asignatura2.obtenerCreditos()}")

    docente1 = Docente("D001", "Dr. Juan Pérez", "Matemáticas")
    docente2 = Docente("D002", "Dra. Ana Gómez", "Física")
    print(docente1.consultarHorario())
    docente1.asignarAsignatura(asignatura1)

    estudiante1 = Estudiante("E001", "Carlos López", "carlos.lopez@universidad.edu")
    print(f"Estudiante {estudiante1.nombre} solicitando matrícula...")

    print(f"¿Horario 1 disponible frente a horario 2?: {horario1.validarDisponibilidad(horario2)}")
    print(f"¿Hora válida? {Horario.es_hora_valida(time(8, 0))}")

    paralelo1.agregarEstudiante(1)
    print(f"¿Matutina es una jornada válida? {Paralelo.es_jornada_valida('Matutina')}")

    asignatura1.actualizarDatos("Matemáticas Avanzadas")
    print(f"¿Código de asignatura válido? {Asignatura.es_codigo_valido(asignatura1.codigo)}")
    print(f"¿ID de docente válido?: {Docente.es_id_valido(docente1.id_docente)}")

    estudiante1.solicitar_matricula()
    estudiante1.matricular(paralelo1)
    print(f"¿Correo de estudiante válido?: {Estudiante.es_correo_valido(estudiante1.correo)}")

    estudiante2 = Estudiante("E002", "María Paz", "maria.paz@universidad.edu")
    print(f"Límite inicial de matrículas para {estudiante2.nombre}: {estudiante2.max_matriculas}")

    Estudiante.cambiar_max_matriculas(2)
    print(f"Se modificó 'max_matriculas' en la clase a: {Estudiante.max_matriculas}")
    print(f"Nuevo límite reconocido por {estudiante2.nombre}: {estudiante2.max_matriculas}")