#Programacion Orientada a Objetos
#Fecha: 29/09/2026
#Autor: Richard Andres Soledispa Vivar
#Titulo: Práctica # 2 Python - Clases, objetos, atributos y métodos.

class Horario:
    Institucion = "ULEAM"

    def __init__(self, aula, horaInicio, horaFin):
        self.aula = aula
        self.horaInicio = horaInicio
        self.horaFin = horaFin

    def cambiarAula(self, nuevaAula):
        self.aula = nuevaAula
        print(f"El aula ha sido cambiada a {self.aula}")

    @classmethod
    def cambiarInstitucion(cls, nuevaInstitucion):
        cls.Institucion = nuevaInstitucion
        print(f"La institucion ha sido cambiada a {cls.Institucion}")

    @staticmethod
    def mostrarhorario(horaInicio, horaFin):
        print(f"El horario es de {horaInicio} a {horaFin}")


class Matricula:
    costo = 0

    def __init__(self, idMatricula, fecha, estado):
        self.idMatricula = idMatricula
        self.fecha = fecha
        self.estado = estado

    def cambiarEstado(self, nuevoEstado):
        self.estado = nuevoEstado
        print(f"El estado de la matricula ha sido cambiado a {self.estado}")

    @classmethod
    def cambiarCosto(cls, nuevoCosto):
        cls.costo = nuevoCosto
        print(f"El costo de la matricula ha sido cambiado a {cls.costo}")

    @staticmethod
    def mostrarMatricula(idMatricula, fecha):
        print(f"La matricula con ID {idMatricula} fue realizada el {fecha}")


class Asignatura:
    creditos = 0

    def __init__(self, nombre, codigo,):
        self.nombre = nombre
        self.codigo = codigo

    def cambiarNombre(self, nuevoNombre):
        nombreAnterior = self.nombre
        self.nombre = nuevoNombre
        print(f"El nombre de la asignatura '{nombreAnterior}' ha sido cambiado a '{self.nombre}'")

    @classmethod
    def cambiarCreditos(cls, nuevosCreditos):
        cls.creditos = nuevosCreditos
        print(f"Los creditos de la asignatura han sido cambiados a {cls.creditos}")

    @staticmethod
    def mostrarAsignatura(nombre, codigo):
        print(f"La asignatura {nombre} tiene el codigo {codigo}")


class Paralelo:
    capacidad = 45  

    def __init__(self, nombre, aula,):
        self.nombre = nombre  
        self.aula = aula

    def cambiarAula(self, nuevaAula):
        self.aula = nuevaAula
        print(f"El paralelo {self.nombre} ahora está asignado al aula {self.aula}")

    @classmethod
    def cambiarCapacidad(cls, nuevaCapacidad):
        cls.capacidad = nuevaCapacidad
        print(f"La capacidad máxima del paralelo se actualizó a {cls.capacidad} estudiantes")

    @staticmethod
    def esCupoValido(cantidadEstudiantes):
        return cantidadEstudiantes <= Paralelo.capacidad


class Docente:
    tituloDocente = "Ingeniero"

    def __init__(self, cedula, nombre, especialidad):
        self.cedula = cedula
        self.nombre = nombre
        self.especialidad = especialidad

    def cambiarEspecialidad(self, nuevaEspecialidad):
        self.especialidad = nuevaEspecialidad
        print(f"La especialidad del docente {self.nombre} ha cambiado a: {self.especialidad}")

    @classmethod
    def cambiarTituloDocente(cls, nuevoTitulo):
        cls.tituloDocente = nuevoTitulo
        print(f"El título del docente ahora es: {cls.tituloDocente}")

    @staticmethod
    def validarCedula(cedula):
        return len(str(cedula)) == 10

# Horario
print("=== Clase Horario ===")
horario1 = Horario(aula="Laboratorio 1", horaInicio="07:00", horaFin="09:00")
print(f"Aula: {horario1.aula}")
horario1.cambiarAula("Laboratorio 3")
Horario.mostrarhorario("07:00", "09:00")
print()

# Matricula
print("=== Clase Matricula ===")
matricula1 = Matricula(idMatricula="M-001", fecha="2026-05-10", estado="Pendiente")
print(f"Estado inicial: {matricula1.estado}")
matricula1.cambiarEstado("Aprobada")
Matricula.mostrarMatricula(matricula1.idMatricula, matricula1.fecha)
print()

# Asignatura
print("=== Clase Asignatura ===")
asignatura1 = Asignatura(nombre="Base de Datos", codigo="BDD-101")
asignatura1.cambiarNombre("Programación Orientada a Objetos")
Asignatura.mostrarAsignatura(asignatura1.nombre, asignatura1.codigo)
print()

# Paralelo
print("=== Clase Paralelo ===")
paralelo1 = Paralelo(nombre="A", aula="Aula 202")
paralelo1.cambiarAula("Aula 205")
es_valido = Paralelo.esCupoValido(40)
print(f"¿40 estudiantes entran en la capacidad?: {es_valido}")
print()

# Docente
print("=== Clase Docente ===")
docente1 = Docente(cedula="1312345678", nombre="Carlos Vera", especialidad="Ingeniero")
docente1.cambiarEspecialidad("Magister")
cedula_valida = Docente.validarCedula(docente1.cedula)
print(f"¿Cédula válida?: {cedula_valida}")
print()

#Ejemplo con atributo de clase de Matricula
m1 = Matricula("M-002", "2026-06-01", "Registrada")

print(f"Costo inicial de la primer matricula: ${m1.costo}") 
print(m1.costo)
Matricula.cambiarCosto(50.00)
print(m1.costo)