from modelos.aulas.creadores.creador_aula import CampoAula, CreadorAula
from modelos.aulas.sala_sustentacion import SalaSustentacion


class CreadorSalaSustentacion(CreadorAula):
    clave = "SUSTENTACION"
    nombre = "Sala de sustentación"

    def campos_adicionales(self) -> tuple[CampoAula, ...]:
        return (CampoAula("tiene_grabacion", "¿Tiene equipo de grabación?", "booleano"),)

    def crear_aula(self, codigo_aula, capacidad, piso, tiene_proyector, **extras) -> SalaSustentacion:
        extras = self._extras_requeridos(extras)
        return SalaSustentacion(codigo_aula, capacidad, piso, tiene_proyector,
                                extras["tiene_grabacion"])
