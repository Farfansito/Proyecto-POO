from modelos.aulas.auditorio import Auditorio
from modelos.aulas.creadores.creador_aula import CampoAula, CreadorAula


class CreadorAuditorio(CreadorAula):
    clave = "AUDITORIO"
    nombre = "Auditorio"

    def campos_adicionales(self) -> tuple[CampoAula, ...]:
        return (CampoAula("tiene_sonido", "¿Tiene sistema de sonido?", "booleano"),)

    def crear_aula(self, codigo_aula, capacidad, piso, tiene_proyector, **extras) -> Auditorio:
        extras = self._extras_requeridos(extras)
        return Auditorio(codigo_aula, capacidad, piso, tiene_proyector,
                         extras["tiene_sonido"])
