from modelos.usuarios.usuario import Usuario
from modelos.academico.paralelo import Paralelo


class Administrador(Usuario):
    def __init__(self, id, nombre, correo, rol="COORDINADOR"):
        super().__init__(id, nombre, correo)
        if not isinstance(rol, str) or rol.strip() == "":
            raise ValueError("El rol no puede estar vacío.")
        self.rol = rol.strip().upper()

    def abrir_paralelo(self, periodo, nivel, codigo, jornada, cupo_maximo):
        # Paralelo y PeriodoAcademico validan los datos y el estado del periodo
        paralelo = Paralelo(codigo, jornada, cupo_maximo, nivel, periodo)
        periodo.agregar_paralelo(paralelo)
        return paralelo

    def ver_horario(self, periodo):
        # Junta los horarios de todas las asignaciones de todos los paralelos
        horarios = []
        for paralelo in periodo.paralelos:
            for asignacion in paralelo.asignaciones:
                horarios.extend(asignacion.horarios)
        return horarios
