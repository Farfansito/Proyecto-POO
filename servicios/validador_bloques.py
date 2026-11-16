from __future__ import annotations

from servicios.contratos import VerificadorBloques
from servicios.reglas_bloque import ContextoBloque


class ValidadorBloques(VerificadorBloques):
    """Aplica una lista de reglas a un bloque candidato.

    Solo comprueba: no reserva aulas ni agrega horarios. Añadir una regla
    nueva no obliga a modificar esta clase: se le pasa otra ReglaBloque.
    """

    def __init__(self, reglas):
        self._reglas = list(reglas)

    def validar(self, asignacion, candidato, asignaciones, original=None) -> None:
        contexto = ContextoBloque(asignacion, candidato, tuple(asignaciones), original)
        for regla in self._reglas:
            regla.verificar(contexto)