"""Servicio de registro de aulas.

Une el patrón Factory Method con el registro del sistema: elige el creador
según el tipo pedido, le encarga crear el aula y la registra. No conoce
ninguna clase concreta de aula ni de creador (solo abstracciones).
"""
from __future__ import annotations

from typing import Protocol

from modelos.aulas.aula import Aula
from modelos.aulas.creadores.catalogo_creadores import CatalogoCreadores
from modelos.aulas.creadores.creador_aula import CampoAula, CreadorAula


class AlmacenAulas(Protocol):
    """Lo mínimo que el servicio necesita del sistema (lo cumple SistemaSCHOS)."""

    aulas: dict

    def registrar_aula(self, aula: Aula) -> None: ...


class ServicioRegistroAulas:
    def __init__(self, almacen: AlmacenAulas, catalogo: CatalogoCreadores):
        self._almacen = almacen
        self._catalogo = catalogo

    def tipos_disponibles(self) -> list[CreadorAula]:
        return self._catalogo.listar()

    def campos_adicionales(self, clave_tipo: str) -> tuple[CampoAula, ...]:
        return self._catalogo.obtener(clave_tipo).campos_adicionales()

    def registrar_aula(self, clave_tipo: str, codigo_aula: str, capacidad: int,
                       piso: int, tiene_proyector: bool, **extras) -> Aula:
        creador = self._catalogo.obtener(clave_tipo)
        aula = creador.crear_aula(codigo_aula, capacidad, piso, tiene_proyector, **extras)
        self._almacen.registrar_aula(aula)
        return aula

    def consultar_aulas(self) -> list[Aula]:
        return list(self._almacen.aulas.values())
