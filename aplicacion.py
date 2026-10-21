class SistemaSCHOS:
    def __init__(self):
        self.usuarios = {}
        self.aulas = {}
        self.asignaturas = {}
        self.niveles = {}
        self.periodo = None

        self.siguientes_ids = {
            "usuario": 1,
            "asignacion": 1,
            "horario": 1,
            "matricula": 1,
        }

    def nuevo_id(self, entidad):
        if entidad not in self.siguientes_ids:
            raise ValueError("Tipo de entidad no válido.")

        identificador = self.siguientes_ids[entidad]
        self.siguientes_ids[entidad] += 1
        return identificador

    def registrar_usuario(self, usuario):
        if usuario.id in self.usuarios:
            raise ValueError("Ya existe un usuario con ese ID.")

        correo = usuario.correo.strip().lower()

        for registrado in self.usuarios.values():
            if registrado.correo.strip().lower() == correo:
                raise ValueError("Ya existe un usuario con ese correo.")

        self.usuarios[usuario.id] = usuario

    def registrar_aula(self, aula):
        codigo = aula.codigo_aula.strip().upper()

        if codigo in self.aulas:
            raise ValueError("Ya existe un aula con ese código.")

        self.aulas[codigo] = aula

    def registrar_asignatura(self, asignatura):
        codigo = asignatura.codigo.strip().upper()

        if codigo in self.asignaturas:
            raise ValueError("Ya existe una asignatura con ese código.")

        self.asignaturas[codigo] = asignatura

    def registrar_nivel(self, nivel):
        if nivel.numero in self.niveles:
            raise ValueError("Ya existe un nivel con ese número.")

        self.niveles[nivel.numero] = nivel

    def establecer_periodo(self, periodo):
        if self.periodo is not None:
            raise ValueError("Ya se ha establecido un periodo académico.")

        self.periodo = periodo