from __future__ import annotations
import tempfile
from datetime import datetime, time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modelos.aulas.aula import Aula


class Horario:
    def __init__(self, dia: str, hora_inicio: time, hora_fin: time, aula: Aula | None = None):
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.nube = ""            # enlace de clase virtual (opcional)
        self.aula = aula          # "se realiza en" 1 Aula

    def calcular_duracion(self) -> int:
        """Duración en minutos."""
        hoy = datetime.today().date()
        delta = datetime.combine(hoy, self.hora_fin) - datetime.combine(hoy, self.hora_inicio)
        return int(delta.total_seconds() // 60)

    def validar_disponibilidad(self) -> bool:
        return self.aula is not None and self.aula.verificar_disponibilidad(self)

    def detectar_conflicto(self, otro: Horario) -> bool:
        return (self.dia.upper() == otro.dia.upper()
                and self.hora_inicio < otro.hora_fin
                and otro.hora_inicio < self.hora_fin)

    def exportar(self) -> Path:
        """Exporta el horario a un archivo de texto temporal."""
        with tempfile.NamedTemporaryFile("w", suffix=".txt", prefix="horario_",
                                         delete=False, encoding="utf-8") as f:
            f.write(str(self))
            return Path(f.name)

    def __str__(self) -> str:
        aula = f" @ {self.aula}" if self.aula else ""
        return f"{self.dia} {self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}{aula}"