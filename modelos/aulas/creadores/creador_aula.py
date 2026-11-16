from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

from modelos.aulas.aula import Aula

TIPOS_CAMPO = ("texto", "booleano")


@dataclass(frozen=True)
class CampoAula:
    """Describe un dato propio de un tipo de aula (p. ej. el equipamiento)."""

    nombre: str
    etiqueta: str
    tipo: str = "texto"

    def __post_init__(self):
        if self.tipo not in TIPOS_CAMPO:
            raise ValueError(f"tipo de campo no válido: {self.tipo}")


class CreadorAula(ABC):
    """Creador abstracto del patrón Factory Method.

    Define el método de fábrica `crear_aula`: cada creador concreto decide
    qué subclase de Aula instancia. Quien use un CreadorAula solo conoce
    esta abstracción y el producto abstracto `Aula`.
    """

    @property
    @abstractmethod
    def clave(self) -> str:
        """Identificador del tipo; coincide con Aula.tipo() del producto."""

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre legible del tipo de aula, para mostrar en el menú."""

    def campos_adicionales(self) -> tuple[CampoAula, ...]:
        """Datos propios del tipo, además de los comunes a toda Aula."""
        return ()

    @abstractmethod
    def crear_aula(self, codigo_aula: str, capacidad: int, piso: int,
                   tiene_proyector: bool, **extras) -> Aula:
        """Método de fábrica: devuelve una nueva Aula del tipo del creador."""

    def _extras_requeridos(self, extras: dict) -> dict:
        """Exige exactamente los campos adicionales declarados por el creador."""
        esperados = {c.nombre for c in self.campos_adicionales()}
        faltan = esperados - extras.keys()
        sobran = extras.keys() - esperados
        if faltan:
            raise ValueError(f"faltan datos para {self.nombre}: {', '.join(sorted(faltan))}")
        if sobran:
            raise ValueError(f"datos no válidos para {self.nombre}: {', '.join(sorted(sobran))}")
        return extras
