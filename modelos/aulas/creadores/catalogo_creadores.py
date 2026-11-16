from __future__ import annotations

from modelos.aulas.creadores.creador_aula import CreadorAula
from modelos.aulas.creadores.creador_aula_teorica import CreadorAulaTeorica
from modelos.aulas.creadores.creador_auditorio import CreadorAuditorio
from modelos.aulas.creadores.creador_laboratorio import CreadorLaboratorio
from modelos.aulas.creadores.creador_sala_sustentacion import CreadorSalaSustentacion


class CatalogoCreadores:
    """Guarda los creadores disponibles y los entrega por clave de tipo.

    Añadir un tipo de aula nuevo consiste en registrar otro CreadorAula:
    ni el catálogo ni sus clientes cambian.
    """

    def __init__(self):
        self._creadores: dict[str, CreadorAula] = {}

    def registrar(self, creador: CreadorAula) -> None:
        if not isinstance(creador, CreadorAula):
            raise TypeError("el creador debe ser una instancia de CreadorAula")
        clave = creador.clave.strip().upper()
        if clave in self._creadores:
            raise ValueError(f"Ya existe un creador para el tipo {clave}.")
        self._creadores[clave] = creador

    def obtener(self, clave: str) -> CreadorAula:
        try:
            return self._creadores[str(clave).strip().upper()]
        except KeyError:
            raise ValueError(f"Tipo de aula no válido: {clave}") from None

    def listar(self) -> list[CreadorAula]:
        return list(self._creadores.values())


def crear_catalogo_por_defecto() -> CatalogoCreadores:
    """Catálogo con los cuatro tipos de aula actuales de SCHOS."""
    catalogo = CatalogoCreadores()
    for creador in (CreadorAulaTeorica(), CreadorLaboratorio(),
                    CreadorAuditorio(), CreadorSalaSustentacion()):
        catalogo.registrar(creador)
    return catalogo
