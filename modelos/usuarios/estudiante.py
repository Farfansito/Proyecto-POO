from modelos.usuarios.usuario import Usuario
from modelos.academico.matricula import Matricula

class Estudiante(Usuario):
    def __init__(self, id, nombre, correo, cedula, carrera):
        super().__init__(id, nombre, correo)
        # Solo se revisa el formato: 10 dígitos
        if not isinstance(cedula, str) or len(cedula.strip()) != 10 or not cedula.strip().isdigit():
            raise ValueError("La cédula debe tener 10 dígitos.")
        if not isinstance(carrera, str) or carrera.strip() == "":
            raise ValueError("La carrera no puede estar vacía.")
        self.cedula = cedula.strip()
        self.carrera = carrera.strip()
        self._matriculas = []

    @property
    def matriculas(self):
        return list(self._matriculas)  # copia de la lista

    def solicitar_matricula(self, periodo, id_matricula):
        if periodo.estado != "ABIERTO":
            raise ValueError("El periodo no está abierto.")
        # No puede tener otra matrícula pendiente o confirmada en el mismo periodo
        for m in self._matriculas:
            if m.periodo is periodo and (m.estado == "PENDIENTE" or m.estado == "CONFIRMADA"):
                raise ValueError("El estudiante ya tiene una matrícula activa en este periodo.")
        matricula = Matricula(id_matricula, self, periodo)
        self._matriculas.append(matricula)
        return matricula

    def matricular(self, paralelo):
        # Busca la matrícula pendiente del periodo del paralelo y elige el paralelo
        for m in self._matriculas:
            if m.periodo is paralelo.periodo and m.estado == "PENDIENTE":
                m.agregar_paralelo(paralelo)
                return m
        raise ValueError("No hay una matrícula pendiente en ese periodo.")

    def ver_horario(self, periodo):
        # Solo cuenta la matrícula CONFIRMADA
        horarios = []
        for m in self._matriculas:
            if m.periodo is periodo and m.estado == "CONFIRMADA":
                for asignacion in m.paralelo.asignaciones:
                    horarios.extend(asignacion.horarios)
        return horarios