from modelos.usuarios.usuario import Usuario
from modelos.horarios.disponibilidad_docente import DisponibilidadDocente


class Docente(Usuario):
    def __init__(self, id, nombre, correo, especialidad, max_horas_semanales):
        super().__init__(id, nombre, correo)
        if not isinstance(especialidad, str) or especialidad.strip() == "":
            raise ValueError("La especialidad no puede estar vacía.")
        if type(max_horas_semanales) != int or max_horas_semanales <= 0:
            raise ValueError("El máximo de horas semanales debe ser un entero positivo.")
        self.especialidad = especialidad.strip()
        self.max_horas_semanales = max_horas_semanales
        self._disponibilidades = []
        self._asignaciones = []

    @property
    def disponibilidades(self):
        return list(self._disponibilidades)  # copia de la lista

    @property
    def asignaciones(self):
        return list(self._asignaciones)  # copia de la lista

    def agregar_disponibilidad(self, dia, inicio, fin):
        # DisponibilidadDocente valida el día y las horas
        disponibilidad = DisponibilidadDocente(dia, inicio, fin)
        self._disponibilidades.append(disponibilidad)

    def esta_disponible(self, dia, inicio, fin):
        # El bloque debe caber completo en alguna disponibilidad
        for disponibilidad in self._disponibilidades:
            if disponibilidad.cubre(dia, inicio, fin):
                return True
        return False

    def horas_asignadas(self, periodo):
        total = 0
        for asignacion in self._asignaciones:
            if asignacion.paralelo.periodo is periodo:
                total += asignacion.horas_semanales
        return total

    def asignar_asignatura(self, asignacion):
        if asignacion.docente is not self:
            raise ValueError("La asignación es de otro docente.")
        for existente in self._asignaciones:
            if existente is asignacion:
                raise ValueError("El docente ya tiene esa asignación.")
        periodo = asignacion.paralelo.periodo
        total = self.horas_asignadas(periodo) + asignacion.horas_semanales
        if total > self.max_horas_semanales:
            raise ValueError("Se supera el máximo de horas semanales del docente.")
        self._asignaciones.append(asignacion)

    def quitar_asignacion(self, asignacion):
        if asignacion not in self._asignaciones:
            raise ValueError("El docente no tiene esa asignación.")
        self._asignaciones.remove(asignacion)

    def ver_horario(self, periodo):
        horarios = []
        for asignacion in self._asignaciones:
            if asignacion.paralelo.periodo is periodo:
                horarios.extend(asignacion.horarios)
        return horarios

    def consultar_horario(self, periodo):
        return self.ver_horario(periodo)